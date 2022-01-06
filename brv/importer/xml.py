def load_xmls(xmlparser, xmls, outputs = None, descr = None,
              append_vers = None, allow_duplicates = False):

    toolrun_ids = []
    total = 0
    for xmlfile in xmls:
        print('Parsing: {0}'.format(xmlfile))
        cnt, run_ids = xmlparser.parseToDB(xmlfile, outputs, descr, append_vers, allow_duplicates)
        print('Got {0} results from {1}'.format(cnt, xmlfile))
        total += cnt
        toolrun_ids.extend(run_ids)

    return total, toolrun_ids, outputs if outputs is not None else []

