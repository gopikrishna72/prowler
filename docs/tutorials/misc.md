# Miscellaneous
## Prowler Version
Show Prowler version:
```console
prowler <provider> -V/-v/--version
```
## Verbose
Execute Prowler in verbose mode (like in Version 2):
```console
prowler <provider> --verbose
```
## Show only Fails
Prowler can only display the failed findings:
```console
prowler <provider> -q/--quiet
```
## Hide Prowler Banner
Prowler can run without showing its banner:
```console
prowler <provider> -b/--no-banner
```
## Checks
Prowler has checks per provider, there are options related with them:

- List the available checks in the provider:
```console
prowler <provider> --list-checks
```
- Execute specific check(s):
```console
prowler <provider> -c/--checks s3_bucket_public_access
```
- Exclude specific check(s):
```console
prowler <provider> -e/--excluded-checks ec2 rds
```
- Execute checks that appears in a json file:
```json
<checks_list>.json

{
    "<provider>": [
        "<check_name_1",
        "<check_name_2",
        "<check_name_3",
        ...
    ],
    ...
}
```
```console
prowler <provider> -C/--checks-file <checks_list>.json
```

## Severities
Each check of Prowler has a severity, there are options related with it:

- List the available checks in the provider:
```console
prowler <provider> --list-severities
```
- Execute specific severity(s):
```console
prowler <provider> --severity critical high
```

## Service
Prowler has services per provider, there are options related with them:

- List the available services in the provider:
```console
prowler <provider> --list-services
```
- Execute specific service(s):
```console
prowler <provider> -s/--services s3 iam
```
- Exclude specific service(s):
```console
prowler <provider> --excluded-services ec2 rds
```

## Categories
Prowler groups checks in different categories, there are options related with them:

- List the available categories in the provider:
```console
prowler <provider> --list-categories
```
- Execute specific category(s):
```console
prowler  <provider> --categories
```

## AWS

### Scan specific AWS Region
Prowler can scan specific region(s) with:
```console
prowler <provider> -f/--filter-region eu-west-1 us-east-1
```
### Use AWS Profile
Prowler can use your custom AWS Profile with:
```console
prowler <provider> -p/--profile <profile_name>
```
