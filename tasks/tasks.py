from celery import Celery, platforms
from chain import settings
import logging
from multiprocessing import current_process
from asset.models import AssetInfo

from tasks.ansible_2420.runner import AdHocRunner, PlayBookRunner
from tasks.ansible_2420.inventory import BaseInventory

platforms.C_FORCE_ROOT = True
app = Celery('chain')
app.config_from_object('django.conf:settings', )
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


logger = logging.getLogger('tasks')


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@app.task()
def ansbile_tools(assets, tools, modules):
    current_process()._config = {'semprefix': '/mp'}

    inventory = BaseInventory(host_list=assets)
    hostname, retsult_data = [], []
    ret = None
    for i in inventory.hosts:
        hostname.append(i)

    if modules == "script":
        runner = AdHocRunner(inventory)
        tasks = [{"action": {"module": "{}".format(
            modules), "args": "{}".format(tools)}, "name": "script"}, ]
        retsult = runner.run(tasks, "all")

        try:
            ok = retsult.results_raw['ok']
            failed = retsult.results_raw['failed']
            unreachable = retsult.results_raw['unreachable']
            if not ok and not failed:
                ret = unreachable
            elif not ok:
                ret = failed
            else:
                ret = ok
        except Exception as e:
            logger.error("{}".format(e))

        for i, element in enumerate(hostname):
            std, ret_host = [], {}
            try:
                out = ret[element]['script']['stdout']
                if not out:
                    out = ret[element]['script']['stderr']
                std.append("{0}".format(out))
            except Exception as e:
                logger.error(e)
                try:
                    std.append("{0}".format(ret[element]['script']['msg']))
                except Exception as e:
                    logger.error("执行失败{0}".format(e))
            ret_host['hostname'] = element
            ret_host['data'] = ''.join(std)
            retsult_data.append(ret_host)

    elif modules == 'yml':

        runers = PlayBookRunner(playbook_path=tools, inventory=inventory)
        retsult = runers.run()

        try:
            ret = retsult['results_callback']
        except Exception as e:
            logger.error("{}".format(e))
        for i, element in enumerate(hostname):
            std, ret_host = [], {}
            try:
                out = ret[element]['stdout']
                if not out:
                    out = ret[element]['stderr']
                std.append("{0}".format(out))
            except Exception as e:
                logger.error(e)
                try:
                    std.append("{0}".format(ret[element]['msg']))
                except Exception as e:
                    logger.error("执行失败{0}".format(e))
            ret_host['hostname'] = element
            ret_host['data'] = ''.join(std)
            retsult_data.append(ret_host)

    return retsult_data


@app.task()
def ansbile_asset_hardware(ids, assets):
    current_process()._config = {'semprefix': '/mp'}


    inventory = BaseInventory(host_list=assets)
    runner = AdHocRunner(inventory)
    tasks = [
        {"action": {"module": "setup", "args": ""}, "name": "script"},
    ]
    retsult = runner.run(tasks, "all")
    hostname = assets[0]['hostname']


    try:
        data = retsult.results_raw['ok'][hostname]['script']['ansible_facts']
        nodename = data['ansible_nodename']
        disk = "{}".format(str(sum([int(data["ansible_devices"][i]["sectors"]) *
                                    int(data["ansible_devices"][i]["sectorsize"]) / 1024 / 1024 / 1024
                                    for i in data["ansible_devices"] if
                                    i[0:2] in ("vd", "ss", "sd")])) + str(" GB"))
        mem = round(data['ansible_memtotal_mb'] / 1024 )
        cpu = int("{}".format(
            data['ansible_processor_count'] * data["ansible_processor_cores"]))

        system = data['ansible_product_name'] + \
            " " + data['ansible_lsb']["description"]

        AssetInfo.objects.filter(id=ids).update(hostname=nodename,
                                                 disk=disk,
                                                 memory=mem,
                                                 cpu=cpu,
                                                 system=system)

    except Exception as e:
        logger.error(e)
