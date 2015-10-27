__author__ = 'plaggm'
import model
import cherrypy

total_procs = 3
userID0 = "User One"
userID1 = "User Two"
userID2 = "User Three"


class optionGen(object):

    uid = 0
    pc_full = '<span class="form-checkbox-item" style="clear:left;">'\
              '<span class="dragger-item">'\
              '</span>'\
              '<input type="checkbox" class="form-checkbox" id="input_9_*" name="q9_choosePeople[]" value="%PID%" />'\
              '<label id="label_input_9_*" for="input_9_*"> %PID% </label>'\
              '</span>'


    pc_left ='<span class="form-checkbox-item" style="clear:left;"> \n' \
                   '<span class="dragger-item"> \n' \
                   '</span> \n'\
                  '<input type="checkbox" class="form-checkbox" id=input_'
    pc_id = "9_0"
    pc_ns = 'name="'
    pc_name = 'choosePeople[]" value="'
    pc_value = '" />'
    pc_label = '"label_input_' + pc_id + '" for ='
    pc_end = '<label id="label_input_9_0" for="input_9_0"> %Person1% </label>'\
                '</span>'

    def __init__(self, id_list):
        self.formList = []
        for id in id_list:
            self.formList.append(self.pc_full.replace('%PID%',id).replace('*', str(self.uid)))
            #self.pc_full = self.pc_full.replace('*', self.uid)
            self.uid += 1


class MainUI(object):
    @cherrypy.expose
    def index(self):
        full = []
        with open('main.html','r') as htf:
            full = htf.readlines()
        return full
    @cherrypy.expose
    def add_form(self):
        searchUID= "$$$$"
        repUID = userID0
        htmlFull = ""
        with open("ui_form.html", 'r') as jsfile:
            htmlLst = jsfile.readlines()
            htmlFull = jsfile.read()
        #htmlFull = htmlFull.replace(searchUID, repUID)
        htmlFull = list(map(lambda line: line.replace(searchUID,repUID),htmlLst))
        searchUID = "%%%%"
        repUID = "1"
        htmlFull = list(map(lambda line: line.replace(searchUID,repUID),htmlFull))

        opt = optionGen([userID0,userID1,userID2])
        htmlFull = list(map(lambda line: line.replace("!@#$",str(opt.formList)),htmlFull))

        return htmlFull

    @cherrypy.expose
    def add_event(self,**kwargs):
        return "Form submitted!"


if __name__ == '__main__':
   cherrypy.quickstart(MainUI(),'/','app.conf')

   ##ADD JSON COMMUNICATION HERE FOR INTRA_PROCESS COMMUNICATIONS