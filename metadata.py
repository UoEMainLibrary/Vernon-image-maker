class Metadata:

    def __init__(self):
        self.imageNameStr = ""
        self.creatorNameStr = 'Digital Imaging Unit'
        self.accessionNo = ""
        self.creatorNotes = ""
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


    def get_view(self, view_bit):
        '''
        :param view_bit:
        :return:
        '''
        return {
            'l': 'Left',
            't': 'Top',
            'q': 'Quarter view',
            's': 'Side View',
            'r': 'Right',
            'f': 'Front',
            'b': 'Back',
            'u': 'Underneath',
            'd': 'Case',
            'g': 'General view',
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
        '''

        :param detail_view_bit:
        :return:
        '''
        return {
            'xs': 'Detail view - stamp or other inscription',
            'xm': 'Detail view - mouthpiece',
            'xp': 'Detail view - painting or other illustrative decoration',
            'xn': 'Detail view'
        }[detail_view_bit]

    def get_suffix(self, format):
        '''
        :param format:
        :return:
        '''
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
        print(url)
        myopener = MyOpener()
        response = myopener.open(url)
        try:
            data = response.read().decode("utf-8")
            return json.loads(data)
        except Exception:
            print("nothing to run")

    def get_creator_notes(self, creator_bit):
        '''
        :param creator_bit:
        :return:
        '''
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
            'k': 'Digital images',
            'l': 'Digital images'
        }[creator_bit]

    def get_name(self, vernon_items):
        '''
        :param vernon_items:
        :return:
        '''
        try:
            name = vernon_items["_embedded"]["records"][0]['name']
            if "\n" in name:
                name = name.replace("\n"," ")
        except Exception:
            name = ''
        return name

    def get_sysid (self, vernon_items):
        '''
        :param vernon_items:
        :return:
        '''
        try:
            id = vernon_items["_embedded"]["records"][0]['id']
        except Exception:
            id = ''
        return id

    def get_date (self, vernon_items):
        '''
        :param vernon_items:
        :return:
        '''
        try:
            date = vernon_items["_embedded"]["records"][0]['prod_pri_date_details_group'][0]['prod_pri_date']
        except Exception:
            date = ''
        return date


    def get_maker (self, vernon_items):
        '''
        :param vernon_items:
        :return:
        '''
        try:
            maker = vernon_items["_embedded"]["records"][0]['prod_pri_person_details_group'][0]['prod_pri_person_name']
        except Exception:
            maker = 'Unknown'
        return maker

    def get_seven_digit (self, vernon_items):
        '''
        :param vernon_items:
        :return:
        '''
        try:
            seven = vernon_items["_embedded"]["records"][0]['user_sym_37']
        except Exception:
            seven = ''
        return seven

    def get_existing_images (self, vernon_items):
        '''
        :param vernon_items:
        :return:
        '''
        try:
            avs = vernon_items["_embedded"]["records"][0]['av_group']
        except Exception:
            avs = ''
        return avs

    def get_creator(self, creator_bit):
        '''
        :param creator_bit:
        :return:
        '''
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
            'k': 'Silke Dykstra',
            'l': 'Zeo Cordey'
        }[creator_bit]

    def derive_tail(self, image_list, accession_no):
        '''
        :param image_list:
        :param accession_no:
        :return:
        '''
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
        '''
        :param existing_images:
        :return:
        '''
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
        from urllib.request import FancyURLopener
        import json
        vernon_api = 'http://vernonapi.is.ed.ac.uk/vcms-api/oecgi4.exe/datafiles/AV/?query='

        class MyOpener(FancyURLopener):
            """
            MyOpener
            """
            version = 'My new User-Agent'

        url = vernon_api + "search:" + searchAV +"&fields=id,im_ref"
        print(url)
        myopener = MyOpener()
        response = myopener.open(url)
        try:
            data = response.read().decode("utf-8")
            return json.loads(data)
        except Exception:
            print("nothing to run")

    def get_items_for_link(self, avNumber):
        from urllib.request import FancyURLopener
        import json
        vernon_api = 'http://vernonapi.is.ed.ac.uk/vcms-api/oecgi4.exe/datafiles/OBJECT/?query='

        class MyOpener(FancyURLopener):
            """
            MyOpener
            """
            version = 'My new User-Agent'

        url = vernon_api + "search:" + avNumber +"&fields=id"
        print(url)
        myopener = MyOpener()
        response = myopener.open(url)
        try:
            data = response.read().decode("utf-8")
            return json.loads(data)
        except Exception:
            print("nothing to run")

    def get_av_sysid(self, vernon_av_items):
        '''
        :param vernon_items:
        :return:
        '''
        try:
            id = vernon_av_items["_embedded"]["records"][0]['id']
        except Exception:
            id = ''
        return id

    def get_work_record_id(self, vernon_items):
        '''
        :param vernon_items:
        :return:
        '''
        try:
            work_record_id = vernon_items["_embedded"]["records"][0]['user_sym_20']
        except Exception:
            work_record_id = ''
        return work_record_id

    def get_repro_rights(self, creator_bit):
        '''
        :param creator_bit:
        :return:
        '''
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

    def get_luna_items(self, imageNameStr):
        from urllib.request import FancyURLopener
        import json
        luna_api = 'https://images.is.ed.ac.uk/luna/servlet/as/fetchMediaSearch?fullData=true&bs=10000&q=Repro_Record_ID='

        class MyOpener(FancyURLopener):
            """
            MyOpener
            """
            version = 'My new User-Agent'

        url = luna_api + imageNameStr
        print(url)
        myopener = MyOpener()
        response = myopener.open(url)
        try:
            data = response.read().decode("utf-8")
            return json.loads(data)
        except Exception:
            print("nothing to run")

    def get_luna_url(self, luna_items):
        '''
        :param creator_bit:
        :return:
        '''
        try:
            luna_url = luna_items[0]['identity']
        except Exception:
            luna_url = ''
        return luna_url
