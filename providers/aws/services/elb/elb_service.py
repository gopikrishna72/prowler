import threading
from typing import Optional

from pydantic import BaseModel

from lib.logger import logger
from providers.aws.aws_provider import generate_regional_clients


################### ELB
class ELB:
    def __init__(self, audit_info):
        self.service = "elb"
        self.session = audit_info.audit_session
        self.regional_clients = generate_regional_clients(self.service, audit_info)
        self.loadbalancers = []
        self.__threading_call__(self.__describe_load_balancers__)

    def __get_session__(self):
        return self.session

    def __threading_call__(self, call):
        threads = []
        for regional_client in self.regional_clients.values():
            threads.append(threading.Thread(target=call, args=(regional_client,)))
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    def __describe_load_balancers__(self, regional_client):
        logger.info("ELB - Describing load balancers...")
        try:
            describe_elb_paginator = regional_client.get_paginator(
                "describe_load_balancers"
            )
            for page in describe_elb_paginator.paginate():
                for elb in page["LoadBalancerDescriptions"]:
                    listeners = []
                    for listener in elb["ListenerDescriptions"]:
                        listeners.append(
                            Listener(
                                protocol=listener["Listener"]["Protocol"],
                                policies=listener["PolicyNames"],
                            )
                        )
                    self.loadbalancers.append(
                        LoadBalancer(
                            name=elb["LoadBalancerName"],
                            dns=elb["DNSName"],
                            region=regional_client.region,
                            scheme=elb["Scheme"],
                            listeners=listeners,
                        )
                    )

        except Exception as error:
            logger.error(
                f"{regional_client.region} -- {error.__class__.__name__}[{error.__traceback__.tb_lineno}]: {error}"
            )


class Listener(BaseModel):
    protocol: str
    policies: list[str]


class LoadBalancer(BaseModel):
    name: str
    dns: str
    region: str
    scheme: str
    listeners: list[Listener]


################### ELBv2
class ELBv2:
    def __init__(self, audit_info):
        self.service = "elbv2"
        self.session = audit_info.audit_session
        self.regional_clients = generate_regional_clients(self.service, audit_info)
        self.loadbalancersv2 = []
        self.__threading_call__(self.__describe_load_balancers__)
        self.listeners = []
        self.__threading_call__(self.__describe_listeners__)
        self.__threading_call__(self.__describe_load_balancer_attributes__)

    def __get_session__(self):
        return self.session

    def __threading_call__(self, call):
        threads = []
        for regional_client in self.regional_clients.values():
            threads.append(threading.Thread(target=call, args=(regional_client,)))
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    def __describe_load_balancers__(self, regional_client):
        logger.info("ELBv2 - Describing load balancers...")
        try:
            describe_elbv2_paginator = regional_client.get_paginator(
                "describe_load_balancers"
            )
            for page in describe_elbv2_paginator.paginate():
                for elbv2 in page["LoadBalancers"]:
                    self.loadbalancersv2.append(
                        LoadBalancerv2(
                            name=elbv2["LoadBalancerName"],
                            region=regional_client.region,
                            arn=elbv2["LoadBalancerArn"],
                            scheme=elbv2["Scheme"],
                            type=elbv2["Type"],
                            listeners=[],
                        )
                    )
        except Exception as error:
            logger.error(
                f"{regional_client.region} -- {error.__class__.__name__}[{error.__traceback__.tb_lineno}]: {error}"
            )

    def __describe_listeners__(self, regional_client):
        logger.info("ELBv2 - Describing listeners...")
        try:
            for lb in self.loadbalancersv2:
                if lb.region == regional_client.region:
                    describe_elbv2_paginator = regional_client.get_paginator(
                        "describe_listeners"
                    )
                    for page in describe_elbv2_paginator.paginate(
                        LoadBalancerArn=lb.arn
                    ):
                        for listener in page["Listeners"]:
                            port = 0
                            if "Port" in listener:
                                port = listener["Port"]
                            lb.listeners.append(
                                Listenerv2(
                                    region=regional_client.region,
                                    arn=listener["ListenerArn"],
                                    port=port,
                                    protocol=listener["Protocol"],
                                )
                            )
        except Exception as error:
            logger.error(
                f"{regional_client.region} -- {error.__class__.__name__}[{error.__traceback__.tb_lineno}]: {error}"
            )

    def __describe_load_balancer_attributes__(self, regional_client):
        logger.info("ELBv2 - Describing attributes...")
        try:
            for lb in self.loadbalancersv2:
                if lb.region == regional_client.region:
                    for attribute in regional_client.describe_load_balancer_attributes(
                        LoadBalancerArn=lb.arn
                    )["Attributes"]:
                        if attribute["Key"] == "routing.http.desync_mitigation_mode":
                            lb.desync_mitigation_mode = attribute["Value"]
                        if attribute["Key"] == "deletion_protection.enabled":
                            lb.deletion_protection = attribute["Value"]
                        if (
                            attribute["Key"]
                            == "routing.http.drop_invalid_header_fields.enabled"
                        ):
                            lb.drop_invalid_header_fields = attribute["Value"]
        except Exception as error:
            logger.error(
                f"{regional_client.region} -- {error.__class__.__name__}[{error.__traceback__.tb_lineno}]: {error}"
            )


class Listenerv2(BaseModel):
    arn: str
    region: str
    port: int
    protocol: str


class LoadBalancerv2(BaseModel):
    name: str
    arn: str
    region: str
    scheme: str
    type: str
    desync_mitigation_mode: Optional[str]
    deletion_protection: Optional[str]
    drop_invalid_header_fields: Optional[str]
    listeners: list[Listenerv2]
