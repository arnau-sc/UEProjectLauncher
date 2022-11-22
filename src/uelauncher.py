import dearpygui.dearpygui as dpg
from tkinter import filedialog as fd 
import os
import configparser
import sys
from pathlib import Path
import webbrowser

#always needs to happen first
dpg.create_context()

version="1.0.0"

#window icons



if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    bundle_dir = Path(sys._MEIPASS)
else:
    bundle_dir = Path(__file__).parent


iconpath = Path.cwd() / bundle_dir / "res/icon.ico"

print(iconpath)

iconsmall = iconpath
iconlarge = iconpath

#end windows icons

def str2bool(string):
    if string == "True":
        return True
    elif string == "False":
        return False
    else:
        raise ValueError("cant convert {"+string+"} to a boolean in str2bool.")

#configparser
userfolder = os.getenv("APPDATA")
userfolder = userfolder.replace(os.sep, "/")
userconfigpath = userfolder+"/UEProjectLauncher/defaultconfig.ini"
cfg = configparser.ConfigParser()
currentpath = ""
currentenginepath = ""

def loadConfig():
    cfg.read(userconfigpath)
    global currentpath
    global currentenginepath
    currentpath = cfg.get("projectpath", "uproject")
    currentenginepath = cfg.get("projectpath", "engine")
    dpg.set_value("log", str2bool(cfg.get("launcheroptions", "log")))
    dpg.set_value("nosound", str2bool(cfg.get("launcheroptions", "nosound")))
    dpg.set_value("skipcompile", str2bool(cfg.get("launcheroptions", "skipcompile")))
    dpg.set_value("runtype", cfg.get("launcheroptions", "runtype"))
    dpg.set_value("customflags", cfg.get("launcheroptions", "customflags"))

    setPathTextProject(currentpath)
    setPathTextEngine(currentenginepath)

if os.path.exists(userconfigpath):
    print(userconfigpath+" exists!")
    
else:
    try:
        os.mkdir(userfolder+"/UEProjectLauncher/")
    except FileExistsError:
        print("config directory exists!")
    
    cfg.read(userconfigpath)

    cfg.add_section("projectpath")
    cfg.set("projectpath", "uproject", "nodefaultpath")
    cfg.set("projectpath", "engine", "nodefaultpath")
    cfg.add_section("launcheroptions")
    cfg.set("launcheroptions", "nosound", "False")
    cfg.set("launcheroptions", "log", "False")
    cfg.set("launcheroptions", "skipcompile", "False")
    cfg.set("launcheroptions", "runtype", "game")
    cfg.set("launcheroptions", "customflags", "")
    with open(userconfigpath, "w") as cfgobj:
        cfg.write(cfgobj)
        cfgobj.close()

#end configparser

def saveConfig():
    
    global currentpath
    global currentenginepath
    cfg.read(userconfigpath)
    
    cfg.set("projectpath", "uproject", currentpath)
    cfg.set("projectpath", "engine", currentenginepath)

    cfg.set("launcheroptions", "nosound", str(dpg.get_value("nosound")))
    cfg.set("launcheroptions", "log", str(dpg.get_value("log")))
    cfg.set("launcheroptions", "skipcompile", str(dpg.get_value("skipcompile")))
    cfg.set("launcheroptions", "runtype", str(dpg.get_value("runtype")))
    cfg.set("launcheroptions", "customflags", str(dpg.get_value("customflags")))
    with open(userconfigpath, "w") as cfgobj:
        cfg.write(cfgobj)
        cfgobj.close()
    print("Saved")
    

def pathExists(path):
    try:
        with open(path, "r", errors="ignore") as testread:
            testread.read()
            return True
    except FileNotFoundError:
        return False

def setPathTextProject(text):
    if pathExists(text):
        dpg.set_value("pathtext", "Selected .uproject: "+text)
    else:
        dpg.set_value("pathtext", "Invalid Path! Please reselect uproject")

def setPathTextEngine(text):
    if pathExists(text):
        dpg.set_value("enginepathtext", "Selected Engine Binary: "+text)
    else:
        dpg.set_value("enginepathtext", "Invalid Path! Please reselect UnrealEditor")



#open file browser to select unrealeditor. Saves the current path to config.
def openFileBrowserEngine():
    global currentenginepath

    enginepath = fd.askopenfilename(initialdir=currentenginepath,title="Select UnrealEditor file", filetypes=(("UnrealEditor.exe files","*.exe"),("all files","*.*")))
    print(enginepath)
    currentenginepath = enginepath
    setPathTextEngine(currentenginepath)
    
    saveConfig()

#open file browser to select .uproject. Saves the current path to config.
def openFileBrowserProject():
    global currentpath

    projectpath = fd.askopenfilename(initialdir=currentpath,title="Select desired .uproject file", filetypes=(("UPROJECT files","*.uproject"),("all files","*.*")))
    print(projectpath)
    currentpath = projectpath
    setPathTextProject(currentpath)

    saveConfig()

def getFlagFromItem(tag):
    cfg.read(userconfigpath)
    if str2bool(cfg.get("launcheroptions", tag)):
        return "-"+tag+" "
    else:
        return ""

def runProject():
    global currentpath
    global currentenginepath
    cfg.read(userconfigpath)
    appendedrunpath = currentenginepath+" "+currentpath+" -"+dpg.get_value("runtype")+" "+getFlagFromItem("log")+getFlagFromItem("nosound")+getFlagFromItem("skipcompile")+dpg.get_value("customflags")

    print(appendedrunpath)
    os.system(appendedrunpath)
    
def openInGithub():
    webbrowser.open("https://github.com/arnau-sc/UEProjectLauncher")


# menu bar
with dpg.viewport_menu_bar():
    with dpg.menu(label="About"):
        dpg.add_text("""With <3 from arnau-sc. Open an issue for any bugs.\nProgram version: """+ version)
        dpg.add_button(label="Open in Github", small=True, callback=openInGithub)

#main dpg window
with dpg.window(tag="Primary Window"):
    
    dpg.add_spacer(height=30)
    dpg.add_button(label="Select UnrealEditor.exe", callback=openFileBrowserEngine)
    dpg.add_text("No default path", tag="enginepathtext")
    dpg.add_button(label="Select UPROJECT file", callback=openFileBrowserProject)
    dpg.add_text("No default path", tag="pathtext")
    dpg.add_separator()
    
    dpg.add_button(label="Run Project!", height=60, width=130, tag="RunButton", callback=runProject)
    with dpg.tooltip("RunButton"):
        dpg.add_text("Run the game with the selected flags")
    
    dpg.add_combo(("game", "editor", "server"), label="Run Type", tag="runtype", width=90, default_value="game", callback=saveConfig)
    
    dpg.add_checkbox(label="Log", tag="log", callback=saveConfig)
    with dpg.tooltip("log"):
        dpg.add_text("Opens separate window to display the contents of the log in real time")    

    dpg.add_checkbox(label="No Sound", tag="nosound", callback=saveConfig)
    with dpg.tooltip("nosound"):
        dpg.add_text("Disables sound")
    
    dpg.add_checkbox(label="Skip Compile", tag="skipcompile", callback=saveConfig)
    with dpg.tooltip("skipcompile"):
        dpg.add_text("""Skips the scripts compilation on editor startup,
useful when launching engine from IDE.""")
    
    dpg.add_separator()
    dpg.add_input_text(label="Custom Flags", tag="customflags", hint="Set your own custom flags. format: -flag1 -flag2 etc.", callback=saveConfig)
    with dpg.tooltip("customflags"):
        dpg.add_text("Set your own custom flags. format: -flag1 -flag2 etc.")


#end main dpg window

loadConfig()

dpg.create_viewport(title='Unreal Project Launcher version: '+version, width=600, height=450)
dpg.set_viewport_small_icon(iconsmall)
dpg.set_viewport_large_icon(iconlarge)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)
dpg.start_dearpygui()
dpg.destroy_context()