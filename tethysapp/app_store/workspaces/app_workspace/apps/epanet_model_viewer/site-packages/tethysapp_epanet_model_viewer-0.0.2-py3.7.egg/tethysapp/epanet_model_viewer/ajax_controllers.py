from django.http import JsonResponse

import os
import tempfile

from multiprocessing import Process, Lock

from hs_restclient import HydroShare
from tethys_services.backends.hs_restclient_helper import get_oauth_hs

from epanettools.epanettools import EPANetSimulation, Node, Link, Control

import uuid
import time

message_template_wrong_req_method = 'This request can only be made through a "{method}" AJAX call.'
message_template_param_unfilled = 'The required "{param}" parameter was not fulfilled.'

mutex = Lock()


def get_epanet_model(request):
    return_obj = {
        'success': False,
        'message': None,
        'results': "",
        'metadata': ""
    }

    if request.is_ajax() and request.method == 'GET':
        if not request.GET.get('model_id'):
            return_obj['message'] = message_template_param_unfilled.format(
                param='model_id')
        else:
            model_id = request.GET['model_id']

            try:
                hs = get_oauth_hs(request)
            except:
                return_obj['message'] = 'You must be logged in through HydroShare to view resources.'
                return JsonResponse(return_obj)

            metadata_json = hs.getScienceMetadata(model_id)
            return_obj['metadata'] = metadata_json

            for model_file in hs.getResourceFileList(model_id):
                model_url = model_file['url']
                model_name = model_url[model_url.find('contents/') + 9:]

                model = ""
                for line in hs.getResourceFile(model_id, model_name):
                    model += line.decode('utf-8')

                return_obj['results'] = model
                return_obj['success'] = True

    else:
        return_obj['message'] = message_template_wrong_req_method.format(
            method="POST")

    return JsonResponse(return_obj)


def upload_epanet_model(request):
    return_obj = {
        'success': False,
        'message': None,
        'results': "",
    }

    if request.is_ajax() and request.method == 'POST':
        try:
            hs = get_oauth_hs(request)
        except:
            return_obj['message'] = 'You must be logged in through HydroShare to view resources.'
            return JsonResponse(return_obj)

        model_title = request.POST['model_title']
        resource_filename = model_title + ".inp"

        abstract = request.POST['model_description'] + \
            '\n{%EPANET Model Repository%}'
        title = model_title

        user_keywords = ["EPANET_2.0"]
        for keyword in request.POST['model_keywords'].split(","):
            user_keywords.append(keyword)
        keywords = (tuple(user_keywords))

        rtype = 'ModelInstanceResource'
        extra_metadata = '{"modelProgram": "EPANET_2.0"}'

        fd, path = tempfile.mkstemp()
        with os.fdopen(fd, 'w') as tmp:
            tmp.write(request.POST['model_file'])
            fpath = path

        metadata = '[{"creator":{"name":"' + hs.getUserInfo()['first_name'] + \
            ' ' + hs.getUserInfo()['last_name'] + '"}}]'

        resource_id = hs.createResource(rtype, title, resource_file=fpath, resource_filename=resource_filename,
                                        keywords=keywords, abstract=abstract, metadata=metadata, extra_metadata=extra_metadata)

        hs.setAccessRules(resource_id, public=True)

        return_obj['results'] = resource_id
        return_obj['success'] = True

    else:
        return_obj['message'] = message_template_wrong_req_method.format(
            method="GET")

    return JsonResponse(return_obj)


def run_epanet_model(request):
    start_time = time.time()

    return_obj = {
        'success': False,
        'message': None,
        'results': "",
    }

    if request.is_ajax() and request.method == 'POST':
        model = request.POST['model']
        quality = request.POST['quality']

        temp = 'tmp_' + str(uuid.uuid4()) + '.inp'

        with open(temp, 'w') as f:
            f.write(model)
        try:
            print("Initializing es")
            es = EPANetSimulation(temp)
            print("--- %s seconds ---" % (time.time() - start_time))
            start_time = time.time()

            print("run")
            es.run()
            print("--- %s seconds ---" % (time.time() - start_time))
            start_time = time.time()

            if quality != "NONE":
                print("runq")
                es.runq()
                print("--- %s seconds ---" % (time.time() - start_time))
                start_time = time.time()

            n = es.network.nodes
            nodes = {}
            node_threads = []
            node_range = 500
            print("getNodeRes")
            if len(n) > node_range:
                process = Process(target=getNodeResults, args=(
                    n, range(1, node_range), nodes))
                process.start()
                node_threads.append(process)

                while node_range < len(n):
                    if len(n) - node_range - 500 < 0:
                        r = range(node_range, len(n) - node_range)
                    else:
                        r = range(node_range, node_range + 500)

                    process = Process(target=getNodeResults,
                                      args=(n, r, nodes))
                    process.start()
                    node_threads.append(process)

                    node_range += 500

            else:
                getNodeResults(n, range(0, len(n)), nodes)

            l = es.network.links
            links = {}
            link_threads = []
            link_range = 500
            if len(l) > link_range:
                process = Process(target=getLinkResults, args=(
                    l, range(1, link_range), links))
                process.start()
                link_threads.append(process)

                while link_range < len(l):
                    if len(l) - link_range - 500 < 0:
                        r = range(link_range, len(l) - link_range)
                    else:
                        r = range(link_range, link_range + 500)

                    process = Process(target=getLinkResults,
                                      args=(l, r, links))
                    process.start()
                    link_threads.append(process)

                    link_range += 500

            else:
                getLinkResults(l, range(0, len(l)), links)

            if len(node_threads) > 0:
                for thread in node_threads:
                    thread.join()
                for thread in link_threads:
                    thread.join()

            print("--- %s seconds ---" % (time.time() - start_time))
            start_time = time.time()

            print("Setting return obj")

            return_obj['results'] = {
                'nodes': nodes,
                'edges': links
            }
            print("--- %s seconds ---" % (time.time() - start_time))

            return_obj['success'] = True

        except Exception as e:
            print(e)
            return_obj[e]

        finally:
            os.remove(temp)

    else:
        return_obj['message'] = message_template_wrong_req_method.format(
            method="POST")

    print("Returning obj")
    return JsonResponse(return_obj)


def getNodeResults(node_list, node_range, nodes):
    with mutex:
        print("Node thread")
        for node in node_range:
            node_id = node_list[node + 1].id

            nodes[node_id] = {}
            nodes[node_id]["EN_QUALITY"] = node_list[node_id].results[12]
            nodes[node_id]["EN_PRESSURE"] = node_list[node_id].results[11]
            nodes[node_id]["EN_HEAD"] = node_list[node_id].results[10]
            nodes[node_id]["EN_DEMAND"] = node_list[node_id].results[9]

        return


def getLinkResults(link_list, link_range, links):
    with mutex:
        print("Link thread")
        for link in link_range:
            link_id = link_list[link + 1].id

            links[link_id] = {}
            links[link_id]["EN_FLOW"] = link_list[link_id].results[8]
            links[link_id]["EN_VELOCITY"] = link_list[link_id].results[9]
            links[link_id]["EN_ENERGY"] = link_list[link_id].results[13]
            links[link_id]["EN_HEADLOSS"] = link_list[link_id].results[10]

        return
