class Metadata:

    def __init__(self):
        self.imageNameStr = ""
        self.creatorNameStr = 'Digital Imaging Unit'
        self.accessionNo = ""
        self.creatorNotes = "Digital images"
        self.viewStr = ""
        self.name = ""
        self.systemid = ""
        self.makerStr = ""
        self.dateStr = ""
        self.imRefStr = ""
        self.masterStr = ""
        self.thumbRef = ""
        self.briefDesc = ""
        self.creditLine = ""
        self.caption = ""
        self.creditLine = "© The University of Edinburgh"
        self.accessionNo = ""
        self.publicationStatus = "Full public access"
        self.collection = "MIMEd"
        self.view_bit = ""
        self.reproRights = "© The University of Edinburgh"
        self.workRecordId = ""
        self.oldId = ""


    def get_view(self, view_bit):
        """
        This function returns a readable string for the view, based on a code
        :param view_bit:
        :return view in string form:
        """
        print(view_bit)
        return {
            'l': 'Left',
            't': 'Top',
            'q': 'Quarter',
            's': 'Side View',
            'r': 'Right',
            'f': 'Front',
            'b': 'Back',
            'u': 'Underneath',
            'd': 'Case',
            'g': 'General',
            'i': 'Insides',
            'o': 'Outsides',
            'c': 'With Case',
            'w': 'Demounted In Sections',
            'z': 'With Accessories',
            'x': 'Detail',
            'e': 'Rosette',
            'n': ''
        }[view_bit]

    def get_detail_view(self, detail_view_bit):
        """
        This function returns the more specific value (based on a two char code) for the detail
        :param detail_view_bit:
        :return detail view in string form:
        """
        return {
            'xs': 'Detail view - stamp or other inscription',
            'xm': 'Detail view - mouthpiece',
            'xp': 'Detail view - painting or other illustrative decoration',
            'xn': 'Detail view'
        }[detail_view_bit]

    def get_suffix(self, format):
        """
        This function returns the DIU suffix applied to jpgs (derivative) and tiffs (crop)
        :param format:
        :return suffix:
        """
        return {
            "tif": "c",
            "tiff": "c",
            "jpg": "d",
            "jpeg": "d",
            "JPG": "d",
            "JPEG": "d",
            "TIF": "c",
            "TIFF": "c"
        }[format]

    def get_items(self, accession_no):
        """
        Get Object info from API and return as json
        :param url: the API URL
        :return data: the returned json
        """
        from urllib.request import FancyURLopener
        import json
        vernon_api = 'http://vernonapi.is.ed.ac.uk/vcms-api/oecgi4.exe/datafiles/OBJECT/?query='

        class MyOpener(FancyURLopener):
            """
            MyOpener
            """
            version = 'My new User-Agent'

        url = vernon_api + "accession_no:" + accession_no + "&fields=id,name,prod_pri_date,prod_pri_person_name,av,user_sym_37,user_sym_20"

        myopener = MyOpener()
        response = myopener.open(url)
        try:
            data = response.read().decode("utf-8")
            return json.loads(data)
        except Exception:
            print("nothing to run")

    def get_creator_notes(self, creator_bit):
        """
        Get the creator notes based on the creator character
        :param creator_bit:
        :return creator notes string:
        """
        return {
            'a': 'Digital images done by ACE',
            'b': 'Greyscale digital images- derived from colour but optimised for monochrome delivery',
            'c': 'Greyscale scans',
            'd': 'Colour digital images',
            'e': 'Digital images',
            'f': 'Digital images',
            'g': 'Greyscale scans from negatives or prints',
            'h': 'Colour digital images and colour scans from negatives or prints',
            'i': 'A camera with gunpowder etc',
            'j': 'Colour digital images',
            'l': 'Digital images',
            'v': 'Digital images'
        }[creator_bit]

    def get_name(self, vernon_items):
        """
        Pick the Title out of the returned JSON array for the Vernon object
        :param vernon_items:
        :return name:
        """
        try:
            name = vernon_items["_embedded"]["records"][0]['name']
            if "\n" in name:
                name = name.replace("\n"," ")
        except Exception:
            name = ''
        return name

    def get_sysid (self, vernon_items):
        """
        Pick the internal Vernon System ID out of the returned JSON array for the Vernon object
        :param vernon_items:
        :return id:
        """
        try:
            id = vernon_items["_embedded"]["records"][0]['id']
        except Exception:
            id = ''
        return id

    def get_av_ref(self, vernon_items):
        """
        Pick the Object Reference (Accession No) out of the returned JSON array for the Vernon object
        :param vernon_items:
        :return ref:
        """
        try:
            ref = vernon_items["_embedded"]["records"][0]['ref_group'][0]['ref']
        except Exception:
            ref = ''
        return ref

    def get_date (self, vernon_items):
        """
        Pick the work creation date out of the returned JSON array for the Vernon object
        :param vernon_items:
        :return date:
        """
        try:
            date = vernon_items["_embedded"]["records"][0]['prod_pri_date_details_group'][0]['prod_pri_date']
        except Exception:
            date = ''
        return date


    def get_maker (self, vernon_items):
        """
        Pick the maker out of the returned JSON array for the Vernon object
        :param vernon_items:
        :return maker:
        """
        try:
            maker = vernon_items["_embedded"]["records"][0]['prod_pri_person_details_group'][0]['prod_pri_person_name']
        except Exception:
            maker = 'Unknown'
        return maker

    def get_seven_digit (self, vernon_items):
        """
        Pick the AV Link ID (seven digit id) out of the returned JSON array for the Vernon object
        :param vernon_items:
        :return seven digit id:
        """
        try:
            seven = vernon_items["_embedded"]["records"][0]['user_sym_37']
        except Exception:
            seven = ''
        return seven

    def get_existing_images (self, vernon_items):
        """
        Pick the list of associated images out of the returned JSON array for the Vernon object
        :param vernon_items:
        :return av_group:
        """
        try:
            avs = vernon_items["_embedded"]["records"][0]['av_group']
        except Exception:
            avs = ''
        return avs

    def get_creator(self, creator_bit):
        """
        Pick the image creator out of the returned JSON array for the Vernon object
        :param creator_bit:
        :return:
        """
        print(creator_bit)
        return {
            'a': 'Rachel Travers',
            'b': 'Raymond Parks',
            'c': 'J. K. Wilkie',
            'd': 'Raymond Parks',
            'e': 'Digital Imaging Unit',
            'f': 'Dominic Ibbotson',
            'g': 'Antonia Reeve',
            'h': 'Antonia Reeve',
            'i': 'Arnold Myers',
            'j': 'Colour digital images',
            'l': 'Silke Dykstra',
            'v': 'Zoe Cordey'
        }[creator_bit]

    def derive_tail(self, image_list, accession_no):
        """
        Work out the tail for an image based on other images for that AV Id
        :param image_list:
        :param accession_no:
        :return newtail:
        """
        batch_tail = 0
        tail_derived = False
        newtail = ''
        for item in image_list:
            list_acc = item["accession"]
            list_tail = item["tail"]
            if list_tail == '':
                list_tail = 0
            if list_acc == accession_no:
                tail_derived = True
                if int(list_tail) > int(batch_tail):
                    batch_tail = list_tail
        if tail_derived == True:
            batch_tail = int(batch_tail) + 1
            newtail = "-" + (str(batch_tail).zfill(4))
        return newtail

    def get_tail(self, existing_images):
        """
        Work out the tail for an image based on other images for that AV Id if the previous function returned null
        :param existing_images:
        :return newtail:
        """
        maxtail = -1
        newtail = "tail"
        avcount = 0
        for av in existing_images:
            avcount += 1
            print(avcount)
            avstring = str(av)
            print(avstring)
            if ";" in avstring:
                av_alls = avstring.split(";")
                av_all = av_alls[0]
                print(av_all)
                if "-" in av_all:
                    av_bits = av_all.split("-")
                    av_bit = av_bits[1]
                    print(av_bit)
                    if "." in av_bit:
                        tailpart = av_bits[1].split(".")
                        tail = tailpart[0]
                        print("T"+tail)
                        if int(tail) > int(maxtail):
                            print(str(tail) + "vs: " + str(maxtail))
                            maxtail = tail
                            print("M"+str(maxtail))
                    else:
                        newtail = ''
                else:
                    newtail = ''
            else:
                newtail = ''

        if avcount == 1:
            if newtail == '':
                newtail = '-0001'

        if avcount == 0:
            newtail = ''

        if avcount > 1:
            if int(maxtail) > -1:
                maxtail = int(maxtail) + 1
                newtail = "-"+(str(maxtail).zfill(4))
        return newtail

    def get_av_items(self, searchAV):
        """
        Get data back for AV ID
        :param searchAV:
        :return data:
        """
        from urllib.request import FancyURLopener
        import json
        vernon_api = 'http://vernonapi.is.ed.ac.uk/vcms-api/oecgi4.exe/datafiles/AV/?query='

        class MyOpener(FancyURLopener):
            """
            MyOpener
            """
            version = 'My new User-Agent'

        url = vernon_api + "search:" + searchAV +"&fields=id,im_ref"
        myopener = MyOpener()
        response = myopener.open(url)
        try:
            data = response.read().decode("utf-8")
            return json.loads(data)
        except Exception:
            print("nothing to run")

    def get_items_for_link(self, avNumber):
        """
        Get data for an av Number
        :param avNumber:
        :return data:
        """
        from urllib.request import FancyURLopener
        import json
        vernon_api = 'http://vernonapi.is.ed.ac.uk/vcms-api/oecgi4.exe/datafiles/OBJECT/?query='

        class MyOpener(FancyURLopener):
            """
            MyOpener
            """
            version = 'My new User-Agent'

        url = vernon_api + "search:" + avNumber +"&fields=id"
        myopener = MyOpener()
        response = myopener.open(url)
        try:
            data = response.read().decode("utf-8")
            return json.loads(data)
        except Exception:
            print("nothing to run")

    def get_av_sysid(self, vernon_av_items):
        """
        Get sysid for an AV from JSON Array
        :param vernon_items:
        :return id:
        """
        try:
            id = vernon_av_items["_embedded"]["records"][0]['id']
        except Exception:
            id = ''
        return id

    def get_work_record_id(self, vernon_items):
        """
        Pick work record id from JSON array of data
        :param vernon_items:
        :return work_record_id:
        """
        try:
            work_record_id = vernon_items["_embedded"]["records"][0]['user_sym_20']
        except Exception:
            work_record_id = ''
        return work_record_id

    def get_repro_rights(self, creator_bit):
        """
        Get the specific rights statement for an image
        :param creator_bit:
        :return string:
        """
        return {
            'a': '© The University of Edinburgh',
            'b': '© The University of Edinburgh',
            'c': '© The University of Edinburgh',
            'd': '© The University of Edinburgh',
            'e': '© The University of Edinburgh',
            'f': '© The University of Edinburgh',
            'g': '© The University of Edinburgh',
            'h': '© The University of Edinburgh',
            'i': '© The University of Edinburgh',
            'j': 'Colour digital images',
            'l': '© Silke Dykstra/The University of Edinburgh',
            'v': '© Zeo Cordey/The University of Edinburgh'
        }[creator_bit]

    def get_link_info(self, imageNameStr):
        """
        Interrogate Vernon API based on an image id
        :param imageNameStr:
        :return data:
        """
        from urllib.request import FancyURLopener
        import json
        vernon_api = 'http://vernonapi.is.ed.ac.uk/vcms-api/oecgi4.exe/datafiles/AV/?query='

        class MyOpener(FancyURLopener):
            """
            MyOpener
            """
            version = 'My new User-Agent'

        url = vernon_api + "search:" + imageNameStr + "&fields=id,im_ref,user_sym_13,user_sym_23,ref"
        print(url)
        myopener = MyOpener()
        response = myopener.open(url)
        try:
            data = response.read().decode("utf-8")
            return json.loads(data)
        except Exception:
            print("nothing to run")

    def get_luna_items(self, imageNameStr):
        """
        Get data back from the LUNA API based on a Repro Record ID
        :param imageNameStr:
        :return data:
        """
        from urllib.request import FancyURLopener
        import json
        luna_api = 'https://images.is.ed.ac.uk/luna/servlet/as/fetchMediaSearch?fullData=true&bs=10000&q=Repro_Record_ID='

        class MyOpener(FancyURLopener):
            """
            MyOpener
            """
            version = 'My new User-Agent'

        url = luna_api + imageNameStr
        myopener = MyOpener()
        response = myopener.open(url)
        try:
            data = response.read().decode("utf-8")
            return json.loads(data)
        except Exception:
            print("nothing to run")

    def get_luna_url(self, luna_items):
        """
        Get the LUNA URL from the returned LUNA json
        :param luna_items:
        :return luna_url:
        """
        try:
            luna_url = luna_items[0]['identity']
        except Exception:
            luna_url = ''
        return luna_url
