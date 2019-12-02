def create_importer(args):
    if args.results_dir:
        return add_from_dir
    elif args.files:
        return add_from_files
    elif args.svcomp:
        return add_from_svcomp

    return None

def create_parser(config_file):
    from brv.xml.parser import XMLParser
    parser = XMLParser(config_file)
    return parser

def add_from_dir(args):
    from brv.importer.dir import load_dir
    parser = create_parser(args.db)
    return load_dir(parser, args.results_dir, args.description, args.append_vers, args.allow_duplicates)

def add_from_files(args):
    from brv.importer.xml import load_xmls
    parser = create_parser(args.db)
    return load_xmls(parser, args.files, args.outputs, args.description,
                      args.append_vers, args.allow_duplicates)

def add_from_svcomp(args):
    from brv.importer.svcomp import load_svcomp
    parser = create_parser(args.db)
    return load_svcomp(parser, args.svcomp, args.description, args.append_vers, args.allow_duplicates)

def tag_runs(toolrun_ids, args):
    if not args.tag:
        return

    from brv.database.writer import DatabaseWriter

    db = DatabaseWriter(args.db)
    tags_str = ';'.join(args.tag)
    print('Tags_str: {}'.format(tags_str))
    for trid in set(toolrun_ids):
        print('Tagging run {}'.format(trid))
        db.setToolRunTags(trid, tags_str)

    db.commit()
    print_col('Tagged {0} tool runs using {1}'.format(len(toolrun_ids), ','.join(args.tag)), "GREEN")

def copy_outputs(outputs, args):
    import os
    # copy the archive with outputs
    if args.scp:
        import scp
        with scp.open_client(args.scp) as client:
            for outfile in outputs:
                client.send_file(os.path.basename(outfile), outfile)
                print('scp {0} --> {1}'.format(outfile, args.scp))
    else:
        for outfile in outputs:
            if not os.path.isdir('outputs'):
                os.mkdir('outputs')

            from shutil import copyfile
            copyfile(os.path.join(path, outfile), os.path.join('outputs/', outfile))
            print('Copied the output: {0}'.format(outfile))


# entrypoint function
def perform_import(args):
    importer = create_importer(args)
    total, toolrun_ids, outputs = importer(args)

    print_col('Added {0} results in total'.format(total), "GREEN")
    tag_runs(toolrun_ids, args)
    copy_outputs(outputs, args)

