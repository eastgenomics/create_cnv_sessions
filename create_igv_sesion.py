#!/usr/bin/env python3

# Script to create IGV sessions for visualisation of CNV calls
from copy import deepcopy
import json

import argparse
import dxpy as dx

def get_url(file_name, project):
    """ Creates download url for a given sample

    Args:
        file_name (_type_): name of file needed
        project (_type_): project of file

    Returns:
        url : dx download url
    """
    file_id = list(dx.bindings.search.find_data_objects(
        project=project,
        name=file_name,
        name_mode='exact'
    ))

    file_info = dx.bindings.dxfile.DXFile(
            dxid=file_id[0]['id'], project=project)

    file_url = file_info.get_download_url(
            duration=604800, preauthenticated=True,
            project=project, filename=file_name)[0]

    return file_url

def main(args):

    DX_PROJECT = 'project-GGPZ4Jj4x2Fy445PFqvYP9xz'

    with open('cnv-template.json') as fh:
        template = json.load(fh)

    template_copy = deepcopy(template)
    template_copy['tracks'] = []

    order_map = {
        '6': {
            'url': '',
            'name': 'CNV-bed',
            'indexURL': ''
        },
        '7': {
            'url': '',
            'indexURL': ''
        },
        '8': {
            'name': 'normal-sample',
            'url': '',
            'indexURL': ''
        },
        '9': {
            'url': '',
            'name': 'variant-bed'
        },
        '10': {
            'url': '',
            'name': 'excluded-regions'
        },
        '11': {
            'url': '',
            'name': 'targets'
        }

    }

    # 6
    filename = args.bam.split('_')[0]
    print(filename)

    order_map['6']['url'] = get_url(
        filename+"_copy_ratios.gcnv.bed.gz", DX_PROJECT)
    order_map['6']['indexURL'] = get_url(
        filename+"_copy_ratios.gcnv.bed.gz.tbi", DX_PROJECT)

    order_map['7']['name'] = filename
    order_map['7']['url'] = get_url(args.bam, DX_PROJECT)
    order_map['7']['indexURL'] = get_url(
        (args.bam+".bai"), DX_PROJECT)

    order_map['8']['url'] = get_url(args.normal, DX_PROJECT)
    order_map['8']['indexURL'] = get_url(
        (args.normal+".bai"), DX_PROJECT)

    order_map['9']['url'] = get_url(
        filename+"_segments_annotated.seg", DX_PROJECT)

    order_map['10']['url'] = get_url(
        args.run + "_excluded_intervals.bed", DX_PROJECT)

    order_map['11']['url'] = get_url(
        "CEN_regions_captured_grch37_v1.0.0.bed",
        "project-Fkb6Gkj433GVVvj73J7x8KbV")

    for track in template['tracks']:
        if track['order'] in [6, 7, 8, 9, 10, 11]:
            order = str(track['order'])
            track['url'] = order_map[order]['url']

        if track['order'] in [6, 7, 8]:
            track['indexURL'] = order_map[order]['indexURL']
        if track['order'] in [6]:
            track['highlightSamples'][filename] = "red"

        template_copy['tracks'].append(track)

    loc = args.cnv.split('_')
    template_copy['locus'] = f'chr{loc[1]}:{loc[2]}-{loc[3]}'


    #for k, v in template_copy.items():
    #    print(k, v)
    output_name = filename + args.cnv + "_igv.json"

    with open(output_name, "w") as outfile:
        json.dump(template_copy, outfile, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--bam')
    parser.add_argument('-p', '--path2reports')
    parser.add_argument('-r', '--run')
    parser.add_argument('-v', '--cnv')
    parser.add_argument('-n', '--normal')

    args = parser.parse_args()

    main(args)
