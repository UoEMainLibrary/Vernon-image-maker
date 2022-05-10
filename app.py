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

@app.route('/downloadrenamecommands')
def download_rename_commands():
    '''
    This function downloads the commands to create renamed files
    '''
    path = "files/rename_commands.txt"
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
        imageBlock = request.form["image_names"].split(",")
        imageType = request.form["image_types"]

        # Derive image types variables
        arnold = False
        diu = False

        if imageType == 'arnold':
            arnold = True

        if imageType == 'diu':
            diu = True

        # Establish XML Trees for Vernon and LUNA
        from xml.dom import minidom
        import xml.etree.cElementTree as ET
        root = ET.Element("recordSet")

        import xml.etree.cElementTree as LUNA_ET
        luna_root = LUNA_ET.Element("recordList")

        # Initialise text files for output
        rename_command_file = open("files/rename_commands.txt", "w")
        image_list_file = open("files/image_list.txt", "w")

        # Initialise image list for tail derivation
        image_list = []

        # Read through images
        for imageNameStr in imageBlock :
            print(imageNameStr)

            newtail = ''

            # Initialise each XML record
            doc = ET.SubElement(root, "record")
            luna_doc = LUNA_ET.SubElement(luna_root, "record")
            metadata = Metadata()

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
                    metadata.viewStr = metadata.viewStr + " " + viewpart.lower()
                    metadata.advanced_view_bit = imageNameStr[10:11]
                    viewpart = metadata.get_view(metadata.advanced_view_bit)
                    metadata.viewStr = metadata.viewStr + " " + viewpart.lower()
                # Parse format of filename and the suffix
                mainext = imageNameStr.split(".")
                format = mainext[1]
                suffix = metadata.get_suffix(format)
                # The imageRef in this case is the whole string
                metadata.imageRef = imageNameStr

            if diu:
                # For DIU images, we need to ask for accession no and view to be provided as well as image name
                # Split these out
                image_bits = imageNameStr.split(":")
                # Accession No is the second bit
                metadata.accessionNo =image_bits[1].lstrip("0")
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


            # Call Vernon API to get JSON payload based on accessionNo
            vernon_items = metadata.get_items(metadata.accessionNo)
            metadata.name = metadata.get_name(vernon_items)
            metadata.systemid = metadata.get_sysid(vernon_items)
            metadata.dateStr = metadata.get_date(vernon_items)
            metadata.makerStr = metadata.get_maker(vernon_items)

            if diu:
                metadata.workRecordId = metadata.get_seven_digit(vernon_items)

            if arnold:
                seven_digit_id = metadata.get_seven_digit(vernon_items)
                metadata.workRecordId = seven_digit_id
                existing_images = metadata.get_existing_images(vernon_items)
                newtail = metadata.derive_tail(image_list, metadata.accessionNo)

                if newtail == '':
                    newtail = metadata.get_tail(existing_images)

            level = 'Crops'
            if suffix == "d":
                level = 'Derivatives'

            metadata.imRefStr = seven_digit_id[0:4] + "000-" + seven_digit_id[0:4] + "999\\" + seven_digit_id + str(suffix) +  newtail + ".jpg"
            metadata.masterStr = "\\\sg.datastore.ed.ac.uk\sg\lib\groups\lac-store\mimed\\" + level + "\\" + seven_digit_id[0:4] + "000-" + seven_digit_id[0:4] + "999\\" + seven_digit_id + str(suffix) + newtail + "." + str(format)
            metadata.caption = seven_digit_id + str(suffix) + newtail + ".jpg" + " (" + metadata.imageRef + ")"
            metadata.briefDesc = metadata.name + " (" + metadata.makerStr + ") : " + metadata.viewStr
            metadata.fileName = seven_digit_id + str(suffix) + newtail + "." + str(format)

            # Build Vernon XML
            ET.SubElement(doc, "im_ref").text = "Image(Electronic)"
            ET.SubElement(doc, "im_format").text = metadata.imRefStr
            ET.SubElement(doc, "master").text = metadata.masterStr
            ET.SubElement(doc, "user_text_2").text = metadata.imageRef
            ET.SubElement(doc, "photographer").text = metadata.creatorNameStr
            ET.SubElement(doc, "notes").text = metadata.creatorNotes
            ET.SubElement(doc, "credit_line").text = metadata.creditLine
            ET.SubElement(doc, "ref").text = str(metadata.accessionNo).zfill(4)
            ET.SubElement(doc, "publication_status").text = metadata.publicationStatus
            ET.SubElement(doc, "collection").text = metadata.collection
            ET.SubElement(doc, "briefDesc").text = metadata.briefDesc
            ET.SubElement(doc, "caption").text = metadata.caption
            ET.SubElement(doc, "thumbRef").text = metadata.imRefStr

            # Build LUNA XML (very complicated set-up)
            field = LUNA_ET.SubElement(luna_doc, "field")
            field.set("name", "work_record_id")
            value = LUNA_ET.SubElement(field, "value")
            value.text = metadata.workRecordId

            entity = LUNA_ET.SubElement(luna_doc, "entity")
            entity.set("name", "id_number")
            field = LUNA_ET.SubElement(entity, "field")
            field.set("name", "catalogue_number")
            value = LUNA_ET.SubElement(field, "value")
            value.text = str(metadata.accessionNo).zfill(4)

            entity = LUNA_ET.SubElement(luna_doc, "entity")
            entity.set("name", "title")
            field = LUNA_ET.SubElement(entity, "field")
            field.set("name", "work_title")
            value = LUNA_ET.SubElement(field, "value")
            value.text = metadata.name

            entity = LUNA_ET.SubElement(luna_doc, "entity")
            entity.set("name", "date")
            field = LUNA_ET.SubElement(entity, "field")
            field.set("name", "work_date")
            value = LUNA_ET.SubElement(field, "value")
            value.text = metadata.dateStr

            entity = LUNA_ET.SubElement(luna_doc, "entity")
            entity.set("name", "creator")
            field = LUNA_ET.SubElement(entity, "field")
            field.set("name", "work_creator_details")
            value = LUNA_ET.SubElement(field, "value")
            value.text = metadata.makerStr

            entity = LUNA_ET.SubElement(luna_doc, "entity")
            entity.set("name", "rights")
            field = LUNA_ET.SubElement(entity, "field")
            field.set("name", "work_rights_statement")
            value = LUNA_ET.SubElement(field, "value")
            value.text = "© The University of Edinburgh"

            '''
            entity = LUNA_ET.SubElement(luna_doc, "entity")
            entity.set("name", "keywords")
            field = LUNA_ET.SubElement(luna_doc, "field")
            field.set("name", "keyword")
            value = LUNA_ET.SubElement(field, "value")
            value.text = metadata.creditLine
            '''

            entity = LUNA_ET.SubElement(luna_doc, "entity")
            entity.set("name", "repro_id_number")
            field = LUNA_ET.SubElement(entity, "field")
            field.set("name", "repro_record_id")
            value = LUNA_ET.SubElement(field, "value")
            value.text = metadata.fileName
            field = LUNA_ET.SubElement(entity, "field")
            field.set("name", "repro_id_number")
            value = LUNA_ET.SubElement(field, "value")
            value.text = metadata.imRefStr
            field = LUNA_ET.SubElement(entity, "field")
            field.set("name", "repro_old_id_number")
            value = LUNA_ET.SubElement(field, "value")
            value.text = metadata.imageNameStr

            entity = LUNA_ET.SubElement(luna_doc, "entity")
            entity.set("name", "repro_title")
            field = LUNA_ET.SubElement(entity, "field")
            field.set("name", "repro_title")
            value = LUNA_ET.SubElement(field, "value")
            value.text = metadata.briefDesc

            entity = LUNA_ET.SubElement(luna_doc, "entity")
            entity.set("name", "repro_rights")
            field = LUNA_ET.SubElement(entity, "field")
            field.set("name", "repro_rights_statement")
            value = LUNA_ET.SubElement(field, "value")
            value.text = metadata.reproRights

            image_list_file.write(metadata.fileName + ",")

            image_list.append({"accession": metadata.accessionNo,
                            "tail": newtail.replace("-","")})

            renameStr = "cp " + metadata.imageRef + " " + metadata.fileName
            rename_command_file.write(renameStr + "\n")

        rough_string = ET.tostring(root, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        pretty_string = reparsed.toprettyxml(indent="\t")
        metadata_file = open("files/vernon.xml", "w")
        metadata_file.write(pretty_string)
        metadata_file.close()

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
        imageBlock = request.form["image_names"].split(",")
        imageType = request.form["image_types"]

        # Derive image types variables
        arnold = False
        diu = False

        if imageType == 'arnold':
            arnold = True

        if imageType == 'diu':
            diu = True

        from xml.dom import minidom
        import xml.etree.cElementTree as ET
        root = ET.Element("recordSet")

        for imageNameStr in imageBlock :
            doc = ET.SubElement(root, "record")
            metadata = Metadata()
            if arnold:
                metadata.avNumber = imageNameStr[1:7]
                vernon_items = metadata.get_items_for_link(metadata.avNumber)

            if diu:
                # For DIU images, we need to ask for accession no and view to be provided as well as image name
                # Split these out
                image_bits = imageNameStr.split(":")
                metadata.accessionNo = image_bits[1].lstrip("0")
                vernon_items = metadata.get_items(metadata.accessionNo)

            metadata.systemid = metadata.get_sysid(vernon_items)
            searchAVBits = imageNameStr.split(".")
            metadata.searchAV = searchAVBits[0]
            vernon_av_items = metadata.get_av_items(metadata.searchAV)
            metadata.av_systemid = metadata.get_av_sysid(vernon_av_items)

            ET.SubElement(doc, "id").text = metadata.systemid
            ET.SubElement(doc, "av").text = metadata.av_systemid

        rough_string = ET.tostring(root, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        pretty_string = reparsed.toprettyxml(indent="\t")
        metadata_file = open("files/vernonlink.xml", "w")
        metadata_file.write(pretty_string)
        metadata_file.close()

    except:
        return Response("error ", sys.exc_info()[0])

    return render_template("public/templates/download_vernon_link.html")

@app.route("/inputiiif", methods=["GET", "POST"])
def input_iiif():

    if request.method == "GET":
        return render_template("public/templates/input_iiif.html")

# add some server side validation in addition to the browser stuff

    try:

        imageBlock = request.form["image_names"].split(",")
        from xml.dom import minidom
        import xml.etree.cElementTree as ET
        root = ET.Element("recordSet")

        for imageNameStr in imageBlock :
            doc = ET.SubElement(root, "record")
            metadata = Metadata()
            metadata.searchAV = imageNameStr.replace(".jpg","")
            metadata.searchAV = imageNameStr.replace(".tif","")
            vernon_av_items = metadata.get_av_items(metadata.searchAV)
            metadata.av_systemid = metadata.get_av_sysid(vernon_av_items)
            luna_items = metadata.get_luna_items(imageNameStr)
            metadata.lunaURL = "https://images.is.ed.ac.uk/luna/servlet/detail/" + metadata.get_luna_url(luna_items)
            metadata.imRefIIIF = metadata.lunaURL.replace('detail', 'iiif') + "/full/full/0/default.jpg"
            metadata.imRefIIIF = metadata.imRefIIIF.replace('https:', 'http:')

            ET.SubElement(doc, "id").text = metadata.av_systemid
            ET.SubElement(doc, "im_ref").text = metadata.imRefIIIF
            ET.SubElement(doc, "luna_url").text = metadata.lunaURL

        rough_string = ET.tostring(root, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        pretty_string = reparsed.toprettyxml(indent="\t")
        metadata_file = open("files/iiif.xml", "w")
        metadata_file.write(pretty_string)
        metadata_file.close()

    except:
        return Response("error ", sys.exc_info()[0])

    return render_template("public/templates/download_iiif.html")


if __name__ == "__main__":
    app.run("0.0.0.0", port=80, debug=True)

