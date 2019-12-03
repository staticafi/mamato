from . xml import load_xmls
import os

def getrundescr(s):
    """
    Return a string that describes the run
    """
    splt = s.split('.')
    # tool + date
    return ('.'.join(splt[:2]), splt[3])


def load_data_with_prefix(xmlparser, path, prefix, xmls, bz2s, outputs, descr, append_vers, allow_duplicates):
    outputs = list(filter(lambda s : s.startswith(prefix), outputs))
    # we must have only one file with outputs
    assert len(outputs) <= 1

    # filter the xmls and prefix with the directory path
    tmp = []
    for x in xmls:
        if not x.startswith(prefix):
            continue


        tmp.append(os.path.join(path, x))
    xmls = tmp

    # unpack the bz2s files
    from bz2 import BZ2File, decompress
    from tempfile import NamedTemporaryFile
    bz2xmls = []
    for bz in bz2s:
        if not bz.startswith(prefix):
            continue

        bzfile = BZ2File(os.path.join(path,bz))
        data = bzfile.read()
        tmpfile = NamedTemporaryFile(suffix='.xml', delete=False)
        tmpfile.write(data)
        bz2xmls.append(tmpfile.name)
        xmls.append(tmpfile.name)
        tmpfile.close()
        bzfile.close()

        print("Decompressed '{0}' to '{1}'".format(bz, tmpfile.name))


    outfile = outputs[0] if outputs else None
    total, toolrun_ids = load_xmls(xmlparser, xmls, outfile, descr,
                      append_vers, allow_duplicates)
    print('Added {0} results'.format(total))

    # clean the temporary xml files
    for f in bz2xmls:
        os.unlink(f)

    # turn filenames into paths (relative or absolute)
    outputs = list(map(lambda p: os.path.join(path, p), outputs))
    return total, toolrun_ids, outputs

def load_dir(xmlparser, path, descr, append_vers, allow_duplicates):
    print("Loading results from {0}".format(path))

    from os import listdir

    xmls = []
    bz2s = []
    outputs = []
    prefixes = set()

    for fl in listdir(path):
        if fl.endswith('.zip'):
            outputs.append(fl)
        elif fl.endswith('.xml'):
            xmls.append(fl)
            prefixes.add(getrundescr(fl))
        elif fl.endswith('.bz2'):
            bz2s.append(fl)
            prefixes.add(getrundescr(fl))

    total = 0
    toolrun_ids = []
    res_outputs = []
    for (prefix, descr) in prefixes:
        print("Found results for: {0}.{1}".format(prefix, descr))
        cnt, runs, outs = load_data_with_prefix(xmlparser, path, prefix, xmls, bz2s, outputs, descr, append_vers, allow_duplicates)
        total += cnt
        toolrun_ids.extend(runs)
        res_outputs.extend(outs)

    return total, toolrun_ids, res_outputs

