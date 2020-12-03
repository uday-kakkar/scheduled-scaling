import argparse
import yaml
import os


parser = argparse.ArgumentParser(description='Generate Kube Spec.')
parser.add_argument('-s', '--service', type=str,
                    help='choose a servicename',required=True)
parser.add_argument('-u', '--scaletime', type=str,
                    help='choose a scaleup cron',required=True)
parser.add_argument('-k', '--keepup', type=int,
                    help='choose a time for keeping scale up',required=True)
parser.add_argument('-m', '--minreplica', type=str,
                    help='choose a template to apply',required=True)
parser.add_argument('-c', '--config', type=str,
                    help='choose a config to apply',required=False)
parser.add_argument('-t', '--template', type=str,
                    help='choose a template to apply',required=True)




def min_max_replica(service):
    with open("ms-limits.yml", 'r') as f:
        ms_data = yaml.load(f,Loader=yaml.FullLoader)
        return ms_data[service]

def populate_template(filename,replacement_dic,scheduler_file_name):
    updated_file = ''
    with open(filename, 'r') as f:
        updated_file = f.read()
        for i, j in replacement_dic.items():
            updated_file = updated_file.replace(i,str(j))
    if not os.path.exists('to_apply'):
        os.makedirs('to_apply')
    with open("to_apply/"+scheduler_file_name, 'w+') as f:
        f.write(updated_file)

def get_replacement_dict(template_name,service,minReplica=None,cron_increment=None):
    min_max_replica_count = min_max_replica(service)
    action_name = template_name.split('template-')[1].split('.yml')[0]
    scheduler_name = "scheduled-{}-{}".format(action_name,service)
    scheduler_file_name = "{}-{}.yml".format(action_name,service)
    scaledown_cron = args.scaletime
    if(cron_increment):
        scaledown_cron = [str(int(args.scaletime.split()[2]) + args.keepup) if i==2 else x for i,x in enumerate(args.scaletime.split())]
        scaledown_cron = ' '.join(scaledown_cron)
    replacement_dic = {"{{MYSCALER}}":scheduler_name,"{{MYSERVICE}}":service,"{{MYSCHEDULESCALEUP}}":args.scaletime,
                        "{{MYUPTARGET}}":minReplica or args.minreplica,"{{MAXREPLICAS}}":min_max_replica_count["maxReplica"],"{{MYSCHEDULESCALEDOWN}}":scaledown_cron,
                        "{{MYDOWNTARGET}}":min_max_replica_count["minReplica"]}
    return {"replacement_dic":replacement_dic,"filename":scheduler_file_name}

def populate_template_single_ms(template,service,minReplica=None):
    templates_used = ["template-scaleup-replicas.yml","template-scaledown-replicas.yml"]
    if (args.template != "template-scaleup-down-replicas.yml"):
        replace_args = get_replacement_dict(template,service,minReplica)
        populate_template(args.template, replace_args["replacement_dic"], replace_args["filename"])
    else:
        for template in templates_used:
            replace_args = get_replacement_dict(template,service,minReplica,args.keepup)
            populate_template(template, replace_args["replacement_dic"], replace_args["filename"])

def populate_template_config(template,conf):
    templates_used = ["template-scaleup-replicas.yml","template-scaledown-replicas.yml"]
    with open(conf, 'r') as f:
        ms_data = yaml.load(f,Loader=yaml.FullLoader)
    for ms in ms_data:
        populate_template_single_ms(template,ms,ms_data[ms]["minReplica"])

if __name__ == "__main__":
    args = parser.parse_args()
    if args.config is None:
        populate_template_single_ms(args.template,args.service)
    else:
        populate_template_config(args.template,args.config)

