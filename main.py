# Standard imports
import argparse
from datetime import datetime
import logging
import sys
import os
import shutil

def GetExecutablePath():
    if getattr(sys, 'frozen', False):
        # Running as a bundled executable
        return os.path.dirname(sys.executable)
    else:
        # Running as a normal .py script
        return os.path.dirname(os.path.abspath(__file__))

class ProjectGenerator:
    exec_path = ''
    rootPath = ''
    logger = None
    definitions = None
    settings = None

    def __init__(self, exec_path: str):
        self.exec_path = exec_path
        configDir = f'{self.exec_path}/config'
        self.definitions = dict()
        self.definitions['year'] = datetime.now().year.__str__()
        self.settings = dict()
        with open(f'{configDir}/comment_header.txt', 'r') as commentHeaderFile:
            content = commentHeaderFile.read() 
            self.definitions['header'] = content

    def AddDefinition(self, fieldName: str, fieldValue: any):
        self.definitions[fieldName] = fieldValue

    def AddSetting(self, fieldName: str, fieldValue: any):
        self.settings[fieldName] = fieldValue

    def SetRootPath(self, rootPath: str):
        self.rootPath = rootPath

    def SetupLogging(self, name: str, path: str) -> logging.Logger:
        self.logger = logging.Logger(name)
        logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-7.7s]  %(message)s")
        self.logger.setLevel(logging.DEBUG)

        fileHandler = logging.FileHandler(path)
        fileHandler.setFormatter(logFormatter)
        self.logger.addHandler(fileHandler)

        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logFormatter)
        self.logger.addHandler(consoleHandler)
        return self.logger

    def CreateDirectory(self, path:str):
        try:
            self.logger.info(f'Creating directory {path}')
            os.makedirs(path, exist_ok=True)
        except Exception as e:
            self.logger.error(f'Cannot create directory {self.rootPath}, exiting...')
            return False
        return True

    def CreateDirectoryExitIfFailed(self, path:str):
        if not self.CreateDirectory(path):
            exit(1)

    def ReplaceField(self, content: str, fieldname: str, definitions: dict):
        loc = content.find(f'{fieldname}')
        if loc != -1:
            if isinstance(definitions[f'{fieldname}'], str):
                content = content.replace(f'{{{fieldname}}}', definitions[f'{fieldname}'])
            elif isinstance(definitions[f'{fieldname}'], list):
                replacement = ''.join([x for x in definitions[f'{fieldname}']])
                content = content.replace(f'{{{fieldname}}}', replacement)
        return content

    def FillInTemplate(self, content: str, definitions: dict):
        content = self.ReplaceField(content, 'header', definitions)
        content = self.ReplaceField(content, 'includes', definitions)
        for fieldName in definitions.keys():
            content = self.ReplaceField(content, fieldName, definitions)
        return content

    def CopyAndFillInTemplate(self, sourcePath: str, destinationPath: str, definitions: dict):
        with open(sourcePath, 'r') as sourceFile:
            content = sourceFile.read()
            filledContent = self.FillInTemplate(content, definitions)
            with open(destinationPath, 'w') as destinationFile:
                destinationFile.write(filledContent)

    def AppendCMakeDirectories(self, path: str, directories: any):
        with open(path, 'r') as cmakeFile:
            content = cmakeFile.read()

        if isinstance(directories, str):
            content += f'add_subdirectory({directories})\n'
        elif isinstance(directories, list):
            content += ''.join([f'add_subdirectory({x})\n' for x in directories])
        with open(path, 'w') as destinationFile:
            destinationFile.write(content)

    def CheckFatal(self, check: bool, message: str):
        if not check:
            self.logger.error(f'{message}')
            self.logger.error(f'Exiting...')
            exit(1)

    def CreateProjectRoot(self) -> bool:
        self.CheckFatal(not os.path.exists(self.rootPath), f'Path {self.rootPath} already exists, will not overwrite.')
        configRoot = f'{self.exec_path}/config'

        projectRoot = self.rootPath
        codeRoot = f'{projectRoot}/code'
        appRoot = f'{codeRoot}/applications'
        libRoot = f'{codeRoot}/libraries'

        self.CreateDirectory(projectRoot)
        definitions = self.definitions.copy()
        template_path = f'{configRoot}/{self.settings['root_cmake_template']}'
        self.CheckFatal(os.path.exists(template_path), 'Non existing template specified for root_cmake_template.')
        self.CopyAndFillInTemplate(template_path, f'{projectRoot}/CMakeLists.txt', definitions)

        self.CreateDirectory(codeRoot)
        definitions = self.definitions.copy()

        template_path = f'{configRoot}/{self.settings['subdir_cmake_template']}'
        cmake_path = f'{codeRoot}/CMakeLists.txt'
        definitions = self.definitions.copy()
        self.CheckFatal(os.path.exists(template_path), 'Non existing template specified for subdir_cmake_template.')
        self.CopyAndFillInTemplate(template_path, cmake_path, definitions)
        self.AppendCMakeDirectories(cmake_path, ['applications', 'libraries'])

        self.CreateDirectory(appRoot)
        definitions = self.definitions.copy()
        self.CheckFatal(os.path.exists(template_path), 'Non existing template specified for app_cmake_template.')
        self.CopyAndFillInTemplate(template_path, f'{appRoot}/CMakeLists.txt', definitions)

        self.CreateDirectory(libRoot)
        definitions = self.definitions.copy()
        self.CheckFatal(os.path.exists(template_path), 'Non existing template specified for lib_cmake_template.')
        self.CopyAndFillInTemplate(template_path, f'{libRoot}/CMakeLists.txt', definitions)

        source_directory = f'{configRoot}/cmake'
        destination_directory = f'{projectRoot}/cmake'
        shutil.copytree(source_directory, destination_directory, dirs_exist_ok=True)

    def CreateApplications(self) -> bool:
        appNames = self.definitions['applications']
        configRoot = f'{self.exec_path}/config'

        applicationsRoot = f'{self.rootPath}/code/applications'
        applicationsCMakeFile = f'{applicationsRoot}/CMakeLists.txt'
        self.CheckFatal(os.path.exists(applicationsCMakeFile), f'Cannot find file {applicationsCMakeFile}.')
        for name in appNames:
            self.logger.info(f'Create application {name}')
            applicationRoot = f'{applicationsRoot}/{name}'
            applicationSourceDir = f'{applicationRoot}/src'
            self.CheckFatal(not os.path.exists(applicationRoot), f'Path {applicationRoot} already exists, will not overwrite.')
            self.CreateDirectory(f'{applicationRoot}')
            self.CreateDirectory(f'{applicationSourceDir}')
            self.CreateDirectory(f'{applicationRoot}/include')

            definitions = self.definitions.copy()
            definitions['filename'] = 'main.cpp'
            definitions['description'] = 'Main {project_name} application source file'
            definitions['class'] = '-'
            definitions['namespace'] = '-'
            definitions['project_name'] = name
            definitions['project_description'] = f'{name} application'

            self.AppendCMakeDirectories(applicationsCMakeFile, definitions['applications'])

            template_path = f'{configRoot}/{self.settings['app_cmake_template']}'
            self.CheckFatal(os.path.exists(template_path), 'Non existing template specified for app_cmake_template.')
            self.CopyAndFillInTemplate(template_path, f'{applicationRoot}/CMakeLists.txt', definitions)

            self.CopyAndFillInTemplate(f'{configRoot}/exe_main.cpp', f'{applicationSourceDir}/main.cpp', definitions)

    def CreateLibraries(self) -> bool:
        libNames = self.definitions['libraries']

        configRoot = f'{self.exec_path}/config'
        librariesRoot = f'{self.rootPath}/code/libraries'
        librariesCMakeFile = f'{librariesRoot}/CMakeLists.txt'
        self.CheckFatal(os.path.exists(librariesCMakeFile), f'Cannot find file {librariesCMakeFile}.')
        for name in libNames:
            self.logger.info(f"Create library {name}")
            libraryRoot = f'{librariesRoot}/{name}'
            librarySourceDir = f'{libraryRoot}/src'
            libraryIncludeDir = f'{libraryRoot}/include/{name}'
            self.CheckFatal(not os.path.exists(librarySourceDir), f'Path {librarySourceDir} already exists, will not overwrite.')
            self.CreateDirectory(f"{libraryRoot}")
            self.CreateDirectory(f"{librarySourceDir}")
            self.CreateDirectory(f"{libraryIncludeDir}")
            self.CreateDirectory(f"{libraryRoot}/test")

            definitions = self.definitions.copy()
            definitions['project_name'] = name
            definitions['project_description'] = f'{name} library'

            self.AppendCMakeDirectories(librariesCMakeFile, name)

            template_path = f'{configRoot}/{self.settings['lib_cmake_template']}'
            self.CheckFatal(os.path.exists(template_path), 'Non existing template specified for lib_cmake_template.')
            self.CopyAndFillInTemplate(template_path, f'{libraryRoot}/CMakeLists.txt', definitions)

            definitions = self.definitions.copy()
            definitions['filename'] = '{libname}.h'
            definitions['class'] = '{libname}Class'
            definitions['description'] = 'Library header file'
            definitions['libname'] = name
            definitions['project_name'] = name
            definitions['project_description'] = f'{name} library'

            self.CopyAndFillInTemplate(f'{configRoot}/lib.h', f'{libraryIncludeDir}/{name}.h', definitions)

            definitions = self.definitions.copy()
            definitions['filename'] = '{libname}.cpp'
            definitions['class'] = '{libname}Class'
            definitions['description'] = 'Library source file'
            definitions['libname'] = name
            definitions['project_name'] = name
            definitions['project_description'] = f'{name} library'
            self.CopyAndFillInTemplate(f'{configRoot}/lib.cpp', f'{librarySourceDir}/{name}.cpp', definitions)

class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(1)

def main():
    program_name = 'CMakeProjectGenerator'
    exec_path = GetExecutablePath()

    generator = ProjectGenerator(exec_path)
    logger = generator.SetupLogging(program_name, f'{exec_path}/log.txt')

    parser = ArgumentParser(prog=program_name, description='CMake project generator for C++')

    # parser.add_argument("name", type=str, help="Your name")
    parser.add_argument('--path', type=str, help='Root project path', default ='.')
    parser.add_argument('--project', type=str, help='Project name (comma separated)', default ='root_project')
    parser.add_argument('--apps', type=str, help='Application names (comma separated)', default ='demo')
    parser.add_argument('--libs', type=str, help='Library names (comma separated)', default ='mylib')
    parser.add_argument('--namespace', type=str, help='Namespace to use for template', default ='ns')
    parser.add_argument('--mode', type=str, help='Namespace to use for template', choices=['project', 'app', 'lib'])
    parser.add_argument('--root-cmake-template', type=str, help='Template to use for root CMake file', default='root_CMakeLists.txt')
    parser.add_argument('--subdir-cmake-template', type=str, help='Template to use for intermediate CMake file', default='subdir_CMakeLists.txt')
    parser.add_argument('--app-cmake-template', type=str, help='Template to use for application CMake file', default='app_CMakeLists.txt')
    parser.add_argument('--lib-cmake-template', type=str, help='Template to use for library CMake file', default='lib_CMakeLists.txt')
    
    # Parse arguments
    try:
        args = parser.parse_args()
    except argparse.ArgumentError as e:
        logger.error(f"Argument parsing error: {e}")

    logger.info(f"{program_name} starting")

    createProjectRoot = False
    createApplication = False
    createLibraries = False

    if args.mode == 'project':
        createProjectRoot = True
        createApplication = True
        createLibraries = True
    elif args.mode == 'app':
        createApplication = True
        if args.apps is None or args.apps == '':
            parser.error('Mode app selected, but no application names specified')

    elif args.mode == 'lib':
        createLibraries = True
        if args.libs is None or args.libs == '':
            parser.error('Mode lib selected, but no library names specified')
    else:
        parser.error('No mode selected')

    rootPath = args.path
    generator.AddDefinition('namespace', args.namespace)
    generator.AddDefinition('applications', args.apps.split(sep=','))
    generator.AddDefinition('libraries', args.libs.split(sep=','))
    generator.AddDefinition('projectname', args.project)
    generator.AddSetting('root_cmake_template', args.root_cmake_template)
    generator.AddSetting('subdir_cmake_template', args.subdir_cmake_template)
    generator.AddSetting('app_cmake_template', args.app_cmake_template)
    generator.AddSetting('lib_cmake_template', args.lib_cmake_template)
    generator.SetRootPath(rootPath)

    if (createProjectRoot):
        generator.CreateProjectRoot()

    if (createApplication):
        generator.CreateApplications()

    if (createLibraries):
        generator.CreateLibraries()

    logger.info(f"{program_name} done.")

if __name__ == "__main__":
    main()
