import json
import sys
import os
from flask import Flask, Response, render_template, request, redirect, url_for, send_from_directory, send_file
from metadata import Metadata

app = Flask(__name__)

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@app.route("/")
def root():
    '''
    This function redirects the default url to "choice"
    '''
    return redirect(url_for('choice'))

@app.route("/choice")
def choice():
    '''
    This function returns the template which offers choices of actions
    '''
    return render_template('public/templates/choice.html')

@app.route('/downloadvernon')
def download_vernon():
    '''
    This function downloads XML for Vernon upload
    '''
    path = "files/vernon.xml"
    return send_file(path, as_attachment=True)

@app.route('/downloadimagelist')
def download_image_list():
    '''
    This function downloads the image list which is used for linking XML
    '''
    path = "files/image_list.txt"
    return send_file(path, as_attachment=True)

@app.route('/downloadvernonlink')
def download_vernon_link():
    '''
    This function downloads the linking XML for Vernon
    '''
    path = "files/vernonlink.xml"
    return send_file(path, as_attachment=True)

@app.route('/downloadluna')
def download_luna():
    '''
    This function downloads the XML for LUNA uploads
    '''
    path = "files/luna.xml"
    return send_file(path, as_attachment=True)

@app.route('/downloadrenamecommandsunix')
def download_rename_commands_unix():
    '''
    This function downloads the commands to create renamed files (UNIX)
    '''
    path = "files/rename_commands_unix.txt"
    return send_file(path, as_attachment=True)

@app.route('/downloadrenamecommandswin')
def download_rename_commands_win():
    '''
    This function downloads the commands to create renamed files (Windows)
    '''
    path = "files/rename_commands_win.txt"
    return send_file(path, as_attachment=True)

@app.route('/downloadiiif')
def download_iiif ():
    '''
    This function downloads the IIIF update XML
    '''
    path = "files/iiif.xml"
    return send_file(path, as_attachment=True)

@app.route("/inputvernon", methods=["GET", "POST"])
def input_vernon():
    '''
    This function does a lot. It creates
        - XML for Vernon import
        - Image List for future stages in the process
        - XML for LUNA import
    It is dependent on the Vernon API to derive information
    '''
    if request.method == "GET":
        return render_template("public/templates/input_vernon.html")
    try:

        # Receive form data (image filenames and image types)
        try:
            imageBlock = request.form["image_names"].split("\r\n")
        except Exception:
            imageBlock = request.form["image_names"].split(",")

        imageType = request.form["image_types"]
        collection = request.form["collection"]

        # Derive image types variables
        arnold = False
        diu = False
        other = False

        if imageType == 'arnold':
            arnold = True

        if imageType == 'diu':
            diu = True

        if imageType == 'other':
            other = True

        # Establish XML Trees for Vernon and LUNA
        from xml.dom import minidom
        import xml.etree.cElementTree as ET
        root = ET.Element("recordSet")

        import xml.etree.cElementTree as LUNA_ET
        luna_root = LUNA_ET.Element("recordList")

        # Initialise text files for output
        rename_command_file_unix = open("files/rename_commands_unix.txt", "w")
        rename_command_file_win = open("files/rename_commands_win.txt", "w")
        image_list_file = open("files/image_list.txt", "w")

        # Initialise image list for tail derivation
        image_list = []

        # Read through images
        for imageNameStr in imageBlock:
            print(repr(imageNameStr))
            imageNameStr.strip()
            print(repr(imageNameStr))

            newtail = ''

            # Initialise each XML record
            doc = ET.SubElement(root, "record")
            luna_doc = LUNA_ET.SubElement(luna_root, "record")
            metadata = Metadata()
            metadata.collection_title = metadata.get_collection_title(collection)
            print(metadata.collection_title)
            collection_folder = collection.lower()
            # Specific processing for Arnold-style images
            if arnold:
                # Creator is identified by the fourth character in the string
                # Three fields can be established from this
                creator_bit = imageNameStr[3:4]
                metadata.creatorNameStr = metadata.get_creator(creator_bit)
                metadata.creatorNotes = metadata.get_creator_notes(creator_bit)
                metadata.reproRights = metadata.get_repro_rights(creator_bit)
                # We are assuming 4-char accession Nos. If there are 1, 2, or 3 accession nos
                # we will need to add that functionality
                metadata.accessionNo = imageNameStr[4:8].lstrip("0")
                # View is identified from the 9th character
                metadata.view_bit = imageNameStr[8:9]
                metadata.viewStr = metadata.get_view(metadata.view_bit)
                # X and Q rely on subsequent characters to get full information
                if metadata.view_bit == 'x':
                    metadata.advanced_view_bit = imageNameStr[8:10]
                    metadata.viewStr = metadata.get_detail_view(metadata.advanced_view_bit)
                if metadata.view_bit == 'q':
                    metadata.advanced_view_bit = imageNameStr[9:10]
                    viewpart = metadata.get_view(metadata.advanced_view_bit)
                    if viewpart:
                        metadata.viewStr = metadata.viewStr + " " + viewpart.lower()
                    metadata.advanced_view_bit = imageNameStr[10:11]
                    viewpart = metadata.get_view(metadata.advanced_view_bit)
                    if viewpart:
                        metadata.viewStr = metadata.viewStr + " " + viewpart.lower()
                    metadata.advanced_view_bit = imageNameStr[11:12]
                    viewpart = metadata.get_view(metadata.advanced_view_bit)
                    if viewpart:
                        metadata.viewStr = metadata.viewStr + " " + viewpart.lower()
                # Parse format of filename and the suffix
                mainext = imageNameStr.split(".")
                format = mainext[1]
                suffix = metadata.get_suffix(format)
                # The imageRef in this case is the whole string
                metadata.imageRef = imageNameStr
                metadata.oldId = imageNameStr

            if diu:
                # For DIU images, we need to ask for accession no and view to be provided as well as image name
                # Split these out
                image_bits = imageNameStr.split(":")
                # Accession No is the second bit
                metadata.accessionNo =image_bits[1]
                print("AC" + metadata.accessionNo)
                # View is the third bit
                metadata.view_bit = image_bits[2]
                print('VB'+metadata.view_bit)
                metadata.viewStr = metadata.get_view(metadata.view_bit[0])
                # X and Q rely on subsequent characters to get full information
                if metadata.view_bit[0] == 'x':
                    metadata.advanced_view_bit = metadata.view_bit[0:2]
                    print("ADV"+metadata.advanced_view_bit)
                    metadata.viewStr = metadata.get_detail_view(metadata.advanced_view_bit)
                if metadata.view_bit[0] == 'q':
                    metadata.advanced_view_bit = metadata.view_bit[1]
                    viewpart = metadata.get_view(metadata.advanced_view_bit)
                    metadata.viewStr = metadata.viewStr + " " + viewpart.lower()
                    metadata.advanced_view_bit = metadata.view_bit[2]
                    viewpart = metadata.get_view(metadata.advanced_view_bit)
                    metadata.viewStr = metadata.viewStr + " " + viewpart.lower()
                try:

                    metadata.creatorNameStr = image_bits[3]
                except Exception:
                    print("defaulting to DIU")

                try:
                    metadata.publicationStatus = metadata.get_pub_status(image_bits[4])
                except Exception:
                    print("defaulting to Full Public Access")

                # Image name is the first bit
                metadata.imageRef = image_bits[0]
                print(metadata.imageRef)
                # Suffix will always be the 8th char
                suffix = metadata.imageRef[7:8]
                print("S" + suffix)
                # Format is part of the image name
                formats = metadata.imageRef.split(".")
                format = formats[1]
                seven_digit_id = metadata.imageRef[0:7]

            if other:
                # For non-DIU, we need to know the
                image_bits = imageNameStr.split(":")
                # Accession No is the second bit
                metadata.accessionNo = image_bits[1]
                print("AC" + metadata.accessionNo)
                # View is the third bit
                metadata.view_bit = image_bits[2]
                print('VB' + metadata.view_bit)
                metadata.viewStr = metadata.get_view(metadata.view_bit[0])
                # X and Q rely on subsequent characters to get full information
                if metadata.view_bit[0] == 'x':
                    metadata.advanced_view_bit = metadata.view_bit[0:2]
                    print("ADV" + metadata.advanced_view_bit)
                    metadata.viewStr = metadata.get_detail_view(metadata.advanced_view_bit)
                if metadata.view_bit[0] == 'q':
                    metadata.advanced_view_bit = metadata.view_bit[1]
                    viewpart = metadata.get_view(metadata.advanced_view_bit)
                    metadata.viewStr = metadata.viewStr + " " + viewpart.lower()
                    metadata.advanced_view_bit = metadata.view_bit[2]
                    viewpart = metadata.get_view(metadata.advanced_view_bit)
                    metadata.viewStr = metadata.viewStr + " " + viewpart.lower()
                try:
                    metadata.creatorNameStr = image_bits[3]
                except Exception:
                    print("defaulting to DIU")

                try:
                    metadata.publicationStatus = metadata.get_pub_status(image_bits[4])
                except Exception:
                    print("defaulting to Full Public Access")

                # Parse format of filename and the suffix
                mainext = image_bits[0].split(".")
                format = mainext[1]
                suffix = metadata.get_suffix(format)
                # The imageRef in this case is the first bit of the string
                metadata.imageRef = image_bits[0]
                print("IMAGEREF" + metadata.imageRef)
                metadata.oldId = image_bits[0]


            # Call Vernon API to get JSON payload based on accessionNo
            vernon_items = metadata.get_items(metadata.accessionNo)
            print(vernon_items)
            metadata.name = metadata.get_name(vernon_items)
            metadata.systemid = metadata.get_sysid(vernon_items)
            metadata.dateStr = metadata.get_date(vernon_items)
            metadata.makerStr = metadata.get_maker(vernon_items)

            if diu:
                metadata.workRecordId = metadata.get_seven_digit(vernon_items)

            if arnold or other:
                print("Arnolding")
                seven_digit_id = metadata.get_seven_digit(vernon_items)
                metadata.workRecordId = seven_digit_id
                existing_images = metadata.get_existing_images(vernon_items)
                print("EXISTING IMAGES")
                print(existing_images)
                #Calculating tails is complicated! First, check if the acc no is already processed in the block.
                #It won't be in Vernon yet, so we just add one to the established highest there.
                #If the image list (processed images) is empty, this will fall over, so check.
                print("IMAGE LIST")
                print(image_list)
                if image_list:
                    newtail = metadata.derive_tail(image_list, metadata.accessionNo)

                print("NEWTAIL" + newtail)
                #If not, generate based on what's in Vernon.
                if newtail == '':
                    newtail = metadata.get_tail(existing_images)

            level = 'Crops'
            if suffix == "d":
                level = 'Derivatives'
            print(metadata.imageRef)
            if "-" in metadata.imageRef:
                full_name = metadata.imageRef[0:len(metadata.imageRef) - 4]
            else:
                full_name = seven_digit_id + str(suffix) + newtail
            print(full_name)

            metadata.imRefStr = seven_digit_id[0:4] + "000-" + seven_digit_id[0:4] + "999\\" + full_name  + ".jpg"
            print(metadata.imRefStr)
            metadata.masterStr = "\\\sg.datastore.ed.ac.uk\sg\lib\groups\lac-store\\" + collection_folder + "\\" + level + "\\" + seven_digit_id[0:4] + "000-" + seven_digit_id[0:4] + "999\\" + full_name + "." + str(format)
            print(metadata.masterStr)

            metadata.caption = full_name + ".jpg" + " (" + metadata.imageRef + ")"
            metadata.briefDesc = metadata.name + " (" + metadata.makerStr + ") : " + metadata.viewStr + " view"
            metadata.fileName = full_name + "." + str(format)

            # Build Vernon XML
            ET.SubElement(doc, "im_format").text = "Image(Electronic)"
            ET.SubElement(doc, "im_ref").text = metadata.imRefStr
            ET.SubElement(doc, "master").text = metadata.masterStr
            if metadata.oldId:
                ET.SubElement(doc, "user_text_2").text = metadata.oldId
            ET.SubElement(doc, "photographer").text = metadata.creatorNameStr
            ET.SubElement(doc, "notes").text = metadata.creatorNotes
            #print(metadata.creditLine)
            #creditParse = metadata.creditLine.encode("ascii", "xmlcharrefreplace")
            #print(creditParse)
            #ET.SubElement(doc, "credit_line").text = creditParse.decode("ascii")
            ET.SubElement(doc, "credit_line").text = metadata.creditLine
            ET.SubElement(doc, "ref").text = str(metadata.accessionNo).zfill(4)
            ET.SubElement(doc, "publication_status").text = metadata.publicationStatus
            ET.SubElement(doc, "collection").text = metadata.collection_title
            #ET.SubElement(doc, "brief_desc").text = metadata.briefDesc.encode("ascii", "xmlcharrefreplace")
            #We are not going to get special characters in most of the metadata, but it's likely here, especially with sharps and flats,
            #which Vernon expects decoded to their html codes before importing. We need to get the character and then turn it into a string from a binary.
            #briefParse = metadata.briefDesc.encode("ascii", "xmlcharrefreplace")
            #ET.SubElement(doc, "brief_desc").text = briefParse.decode("ascii")
            ET.SubElement(doc, "brief_desc").text = metadata.briefDesc
            ET.SubElement(doc, "caption").text = metadata.caption
            ET.SubElement(doc, "thumbref").text = metadata.imRefStr

            # Build LUNA XML (very complicated set-up)
            field = LUNA_ET.SubElement(luna_doc, "field")
            field.set("name", "work_record_id")
            value = LUNA_ET.SubElement(field, "value")
            value.text = metadata.workRecordId
            print(value.text)

            entity = LUNA_ET.SubElement(luna_doc, "entity")
            entity.set("name", "id_number")
            field = LUNA_ET.SubElement(entity, "field")
            field.set("name", "work_catalogue_number")
            value = LUNA_ET.SubElement(field, "value")
            value.text = str(metadata.accessionNo).zfill(4)
            print(value.text)

            entity = LUNA_ET.SubElement(luna_doc, "entity")
            entity.set("name", "title")
            field = LUNA_ET.SubElement(entity, "field")
            field.set("name", "work_title")
            value = LUNA_ET.SubElement(field, "value")
            value.text = metadata.name
            print(value.text)

            entity = LUNA_ET.SubElement(luna_doc, "entity")
            entity.set("name", "creator")
            field = LUNA_ET.SubElement(entity, "field")
            field.set("name", "work_creator_details")
            value = LUNA_ET.SubElement(field, "value")
            value.text = metadata.makerStr
            print(value.text)
            field = LUNA_ET.SubElement(entity, "field")
            field.set("name", "work_creator_name")
            value = LUNA_ET.SubElement(field, "value")
            value.text = metadata.makerStr
            print(value.text)

            entity = LUNA_ET.SubElement(luna_doc, "entity")
            entity.set("name", "dates")
            field = LUNA_ET.SubElement(entity, "field")
            field.set("name", "work_display_date")
            value = LUNA_ET.SubElement(field, "value")
            value.text = metadata.dateStr
            print(value.text)

            entity = LUNA_ET.SubElement(luna_doc, "entity")
            entity.set("name", "rights")
            field = LUNA_ET.SubElement(entity, "field")
            field.set("name", "work_rights_statement")
            value = LUNA_ET.SubElement(field, "value")
            value.text = "© The University of Edinburgh"
            print(value.text)

            '''
            entity = LUNA_ET.SubElement(luna_doc, "entity")
            entity.set("name", "keywords")
            field = LUNA_ET.SubElement(luna_doc, "field")
            field.set("name", "keyword")
            value = LUNA_ET.SubElement(field, "value")
            value.text = metadata.creditLine
            '''

            entity = LUNA_ET.SubElement(luna_doc, "entity")
            entity.set("name", "repro_record")
            field = LUNA_ET.SubElement(entity, "field")
            field.set("name", "repro_record_id")
            value = LUNA_ET.SubElement(field, "value")
            value.text = metadata.fileName
            print(value.text)

            entity = LUNA_ET.SubElement(luna_doc, "entity")
            entity.set("name", "repro_title")
            field = LUNA_ET.SubElement(entity, "field")
            field.set("name", "repro_title")
            value = LUNA_ET.SubElement(field, "value")
            value.text = metadata.briefDesc
            print(value.text)

            entity = LUNA_ET.SubElement(luna_doc, "entity")
            entity.set("name", "repro_id_number")
            field = LUNA_ET.SubElement(entity, "field")
            field.set("name", "repro_id_number")
            value = LUNA_ET.SubElement(field, "value")
            value.text = metadata.imRefStr
            print(value.text)
            field = LUNA_ET.SubElement(entity, "field")
            field.set("name", "repro_old_id_number")
            value = LUNA_ET.SubElement(field, "value")
            value.text = metadata.oldId
            print(value.text)

            entity = LUNA_ET.SubElement(luna_doc, "entity")
            entity.set("name", "repro_creator")
            field = LUNA_ET.SubElement(entity, "field")
            field.set("name", "repro_creator_name")
            value = LUNA_ET.SubElement(field, "value")
            value.text = metadata.creatorNameStr
            print(value.text)
            field = LUNA_ET.SubElement(entity, "field")
            field.set("name", "repro_creator_role_description")
            value = LUNA_ET.SubElement(field, "value")
            value.text = "Creator"

            entity = LUNA_ET.SubElement(luna_doc, "entity")
            entity.set("name", "repro_rights")
            field = LUNA_ET.SubElement(entity, "field")
            field.set("name", "repro_rights_statement")
            value = LUNA_ET.SubElement(field, "value")
            value.text = metadata.reproRights
            print(value.text)

            entity = LUNA_ET.SubElement(luna_doc, "entity")
            entity.set("name", "repro_publication_status")
            field = LUNA_ET.SubElement(entity, "field")
            field.set("name", "repro_publication_status")
            value = LUNA_ET.SubElement(field, "value")
            value.text = "Full public access"

            image_list_file.write(metadata.fileName + ",")

            image_list.append({"accession": metadata.accessionNo,
                            "tail": newtail.replace("-","")})

            renameStrUNIX = "cp " + metadata.imageRef + " " + metadata.fileName
            rename_command_file_unix.write(renameStrUNIX + "\n")

            renameStrUNIX = "copy " + metadata.imageRef + " " + metadata.fileName
            rename_command_file_win.write(renameStrUNIX + "\n")


        #rough_string = ET.tostring(root)
        #brief_parse = rough_string("ascii", "xmlcharrefreplace")
        #parsed_again = brief_parse.decode("ascii")
        #reparsed = minidom.parseString(parsed_again)
        #reparsed = minidom.parseString(rough_string)
        #pretty_string = reparsed.toprettyxml(indent="\t")
        #print(reparsed)
        #metadata_file = open("files/vernon.xml", "w")
        #metadata_file.write(pretty_string)
        #metadata_file.close()

        #Write to XML file. For Vernon, the xml_declaration is crucial, as it expects special chars to be
        #rendered as &#xxx; html codes.
        with open('files/vernon.xml', 'wb') as metadata_file:
            ET.ElementTree(root).write(metadata_file, xml_declaration=True)
        print(LUNA_ET)
        rough_luna_string = LUNA_ET.tostring(luna_root, 'utf-8')
        luna_reparsed = minidom.parseString(rough_luna_string)
        pretty_luna_string = luna_reparsed.toprettyxml(indent="\t")
        luna_metadata_file = open("files/luna.xml", "w")
        luna_metadata_file.write(pretty_luna_string)
        luna_metadata_file.close()

    except:
        return Response("error ", sys.exc_info()[0])

    return render_template("public/templates/download_vernon.html")

@app.route("/inputvernonlink", methods=["GET", "POST"])
def input_vernon_link():

    if request.method == "GET":
        return render_template("public/templates/input_vernon_link.html")

    try:
        images = request.form["image_names"]
        last_char = images[len(images) - 1]
        if last_char == ",":
            images = images[:-1]
        imageBlock = images.split(",")

        print(imageBlock)

        #imageType = request.form["image_types"]

        # Derive image types variables
        #arnold = False
        #diu = False

        #if imageType == 'arnold':
        #    arnold = True

        #if imageType == 'diu':
        #    diu = True

        from xml.dom import minidom
        import xml.etree.cElementTree as ET
        root = ET.Element("recordSet")

        for imageNameStr in imageBlock:
            print(imageNameStr)
            doc = ET.SubElement(root, "record")
            metadata = Metadata()

            #if arnold:
            #    metadata.avNumber = imageNameStr
            #    print(metadata.avNumber)
            #    vernon_items = metadata.get_items_for_link(metadata.avNumber)

            #if diu:
                # For DIU images, we need to ask for accession no and view to be provided as well as image name
                # Split these out
            #vernon_items = metadata.get_items_for_link(imageNameStr[0:7])

            # SR 28/04/2025 - API failing to search with extension to get accession_no
            image_without_extension = imageNameStr.split('.')[0]
            print(image_without_extension)
            vernon_items = metadata.get_link_info(image_without_extension)

            if vernon_items and '_embedded' in vernon_items:
                records = vernon_items['_embedded'].get('records', [])
                if records:
                    first_record = records[0]
                    print(first_record['user_sym_13'])  # Example of accessing a field
                else:
                    print("No records found.")
            else:
                print("Invalid data structure returned.")

            metadata.accessionNo = metadata.get_av_ref(vernon_items)

            metadata.accessionNo = metadata.accessionNo.zfill(4)
            print("AFTER ACCESSIONNO.ZFILL" + metadata.accessionNo)
            object_items = metadata.get_items(metadata.accessionNo)
            print("AFTER GET_ITEMS " + str(object_items))
            metadata.systemid = metadata.get_sysid(object_items)
            print("AFTER GET_SYSID" + metadata.systemid)

            searchAVBits = imageNameStr.split(".")
            metadata.searchAV = searchAVBits[0]
            vernon_av_items = metadata.get_av_items(metadata.searchAV)
            print("AFTER GET_AV_ITEMS" + vernon_av_items)
            metadata.av_systemid = metadata.get_av_sysid(vernon_av_items)

            ET.SubElement(doc, "id").text = metadata.systemid
            ET.SubElement(doc, "av").text = metadata.av_systemid

        rough_string = ET.tostring(root, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        pretty_string = reparsed.toprettyxml(indent="\t")
        metadata_file = open("files/vernonlink.xml", "w")
        metadata_file.write(pretty_string)
        metadata_file.close()

        print("AM I HERE" + imageBlock)

        from xml.dom import minidom
        import xml.etree.cElementTree as ET
        print("I AM BUILDING A TREE")
        root = ET.Element("recordSet")
        for imageNameStr in imageBlock:
            print("AM I HERE?")
            doc = ET.SubElement(root, "record")
            metadata = Metadata()
            metadata.searchAV = imageNameStr.replace(".jpg","")
            metadata.searchAV = imageNameStr.replace(".tif","")
            print(metadata.searchAV)
            vernon_av_items = metadata.get_av_items(metadata.searchAV)
            print(vernon_av_items)
            metadata.av_systemid = metadata.get_av_sysid(vernon_av_items)
            print(metadata.av_systemid)
            luna_items = metadata.get_luna_items(imageNameStr)
            print(luna_items)
            metadata.lunaURL = "https://images.is.ed.ac.uk/luna/servlet/detail/" + metadata.get_luna_url(luna_items)
            metadata.imRefIIIF = metadata.lunaURL.replace('detail', 'iiif') + "/full/full/0/default.jpg"
            metadata.imRefIIIF = metadata.imRefIIIF.replace('https:', 'http:')

            ET.SubElement(doc, "id").text = metadata.av_systemid
            ET.SubElement(doc, "im_ref").text = metadata.imRefIIIF
            ET.SubElement(doc, "luna_url").text = metadata.lunaURL

        iiif_string = ET.tostring(root, 'utf-8')
        reparsed_iiif = minidom.parseString(iiif_string)
        pretty_iiif_string = reparsed_iiif.toprettyxml(indent="\t")
        print("I HAVE PRETTIFIED THE IIIF STRING HAVEN'T I?")
        metadata_file = open("files/iiif.xml", "w")
        metadata_file.write(pretty_iiif_string)
        metadata_file.close()

    except:
        print("error")
        #return Response("error ", sys.exc_info()[0])
    #sys.exc_info()[0]


    return render_template("public/templates/download_vernon_link.html")

@app.route("/getmaxid", methods=["GET", "POST"])
def get_max_id():
    import re
    metadata = Metadata()
    #if request.method == "GET":
    #    return render_template("public/templates/get_max_id.html")

    try:
        data = metadata.get_all_mimed()
        other_id_list = []
        n = 0

        for record in data["_embedded"]["records"]:
            n += 1
            for other_id in record["other_id_group"]:
                other_id_val = other_id["other_id"]
                # if other_id_val[0] == "0" and len(other_id_val) == 7 and other_id_val[6] != ".":
                pattern = re.compile("^0\d{6}$")
                if pattern.match(other_id_val):
                    other_id_list.append(other_id_val)
            max_no = max(other_id_list)
    except:
        return Response("error ", sys.exc_info()[0])

    print(max_no)

    new_max_no = str(int(max_no) + 1).zfill(7)

    print(new_max_no)


    return render_template("public/templates/get_max_id.html", data=new_max_no)

@app.route("/getmaxidart", methods=["GET", "POST"])
def get_max_id_art():
    import re
    metadata = Metadata()
    #if request.method == "GET":
    #    return render_template("public/templates/get_max_id.html")

    try:
        data = metadata.get_all_art()
        other_id_list = []
        n = 0
        for record in data["_embedded"]["records"]:
            n += 1
            for other_id in record["other_id_group"]:
                other_id_val = other_id["other_id"]
                # if other_id_val[0] == "0" and len(other_id_val) == 7 and other_id_val[6] != ".":
                pattern = re.compile("^0\d{6}$")
                if pattern.match(other_id_val):
                    other_id_list.append(other_id_val)
            max_no = max(other_id_list)
    except:
        return Response("error ", sys.exc_info()[0])

    print(max_no)

    new_max_no = str(int(max_no) + 1).zfill(7)

    print(new_max_no)


    return render_template("public/templates/get_max_id_art.html", data=new_max_no)


if __name__ == "__main__":
    app.run("0.0.0.0", port=5002, debug=True)

