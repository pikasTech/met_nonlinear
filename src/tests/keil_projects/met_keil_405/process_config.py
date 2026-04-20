#!pika
# create objects
sg = MET.SignalGenerator()
ps = MET.Process()
saoPin = MET.Scanner()

config = {
    'mode': 'normal',
    'is_use_Wp': False,
    'is_enable_saoPin': True,
    'is_reboot_after_saoPin': True,
}

# config Process
ps.setMode(config['mode'])
if config['is_use_Wp'] :
    ps.enableWp()
else:
    ps.disableWp()

if config['is_enable_saoPin']:
    saoPin.enable()

if config['is_reboot_after_saoPin']:
    saoPin.rebootAfterScanEnable()
    saoPin.setContinue(False)
    
# print config
print('[Config]:')
print(config)
print('Start Process')
saoPin.enable()

exit()
#!pika