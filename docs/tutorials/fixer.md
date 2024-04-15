# Prowler Fixer
Prowler allows you to fix some of the failed findings it identifies. You can use the `--fixer` flag to run the fixes that are available for the checks that failed.

```sh
prowler <provider> -c <check_to_fix_1> <check_to_fix_2> ... --fixer
```

<img src="../img/fixer.png">

???+ note
    You can see all the available fixes for each provider with the `--list-fixers` flag.

    ```sh
    prowler <provider> --list-fixer
    ```

## Writing a Fixer
To write a fixer, you need to create a file called `<check_id>_fixer.py` inside the check folder, with a function called `fixer` that receives either the region or the resource to be fixed as a parameter, and returns a boolean value indicating if the fix was successful or not.

For example, the regional fixer for the `ec2_ebs_default_encryption` check, which enables EBS encryption by default in a region, would look like this:
```python
from prowler.lib.logger import logger
from prowler.providers.aws.services.ec2.ec2_client import ec2_client


def fixer(region):
    """
    Enable EBS encryption by default in a region. NOTE: Custom KMS keys for EBS Default Encryption may be overwritten.
    Requires the ec2:EnableEbsEncryptionByDefault permission:
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "ec2:EnableEbsEncryptionByDefault",
                "Resource": "*"
            }
        ]
    }
    Args:
        region (str): AWS region
    Returns:
        bool: True if EBS encryption by default is enabled, False otherwise
    """
    try:
        regional_client = ec2_client.regional_clients[region]
        return regional_client.enable_ebs_encryption_by_default()[
            "EbsEncryptionByDefault"
        ]
    except Exception as error:
        logger.error(
            f"{region} -- {error.__class__.__name__}[{error.__traceback__.tb_lineno}]: {error}"
        )
        return False
```
On the other hand, the fixer for the `s3_account_level_public_access_blocks` check, which enables the account-level public access blocks for S3, would look like this:
```python
from prowler.lib.logger import logger
from prowler.providers.aws.services.s3.s3control_client import s3control_client


def fixer(resource_id: str) -> bool:
    """
    Enable S3 Block Public Access for the account. NOTE: By blocking all S3 public access you may break public S3 buckets.
    Requires the s3:PutAccountPublicAccessBlock permission:
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "s3:PutAccountPublicAccessBlock",
                "Resource": "*"
            }
        ]
    }
    Returns:
        bool: True if S3 Block Public Access is enabled, False otherwise
    """
    try:
        s3control_client.client.put_public_access_block(
            AccountId=resource_id,
            PublicAccessBlockConfiguration={
                "BlockPublicAcls": True,
                "IgnorePublicAcls": True,
                "BlockPublicPolicy": True,
                "RestrictPublicBuckets": True,
            },
        )
    except Exception as error:
        logger.error(
            f"{error.__class__.__name__}[{error.__traceback__.tb_lineno}]: {error}"
        )
        return False
    else:
        return True
```

## Fixer Config file
For some fixers, you can have configurable parameters depending on your use case. You can either use the default config file in `prowler/config/fixer_config.yaml` or create a custom config file and pass it to the fixer with the `--fixer-config` flag. The config file should be a YAML file with the following structure:
```yaml
# Fixer configuration file
aws:
  # ec2_ebs_default_encryption
    # No configuration needed for this check

  # s3_account_level_public_access_blocks
    # No configuration needed for this check

  # iam_password_policy_* checks:
  iam_password_policy:
      MinimumPasswordLength: 14
      RequireSymbols: True
      RequireNumbers: True
      RequireUppercaseCharacters: True
      RequireLowercaseCharacters: True
      AllowUsersToChangePassword: True
      MaxPasswordAge: 90
      PasswordReusePrevention: 24
      HardExpiry: False
```
