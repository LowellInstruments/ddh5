I am trying to:

- GUI - delete LOG process and be run as thread
- GUI - delete NET process and be run as thread
- GUI - delete 1 timer to check power, redis... run as function when timer_one_sec = 60
- GUI - delete 1 timer to check atcom, run as thread when timer_one_sec = 600
- AWS - delete SQS process and be run as function


test:
- LOG works
- NET works
- SQS works
- check_power_works
- check_atcom_works
- closing DDH works
- opening DDH works

