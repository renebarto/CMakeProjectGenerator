# CMakeProjectGenerator
Generator for standard project structure CMake setup

Generates a folder structure including CMake files.

```text
usage: CMakeProjectGenerator [-h] [--path PATH] [--project PROJECT] [--apps APPS] [--libs LIBS] [--namespace NAMESPACE] [--mode {project,app,lib}] [--root-cmake-template ROOT_CMAKE_TEMPLATE]
                             [--subdir-cmake-template SUBDIR_CMAKE_TEMPLATE] [--app-cmake-template APP_CMAKE_TEMPLATE] [--lib-cmake-template LIB_CMAKE_TEMPLATE]

CMake project generator for C++

options:
  -h, --help            show this help message and exit
  --path PATH           Root project path
  --project PROJECT     Project name (comma separated)
  --apps APPS           Application names (comma separated)
  --libs LIBS           Library names (comma separated)
  --namespace NAMESPACE
                        Namespace to use for template
  --mode {project,app,lib}
                        Namespace to use for template
  --root-cmake-template ROOT_CMAKE_TEMPLATE
                        Template to use for root CMake file
  --subdir-cmake-template SUBDIR_CMAKE_TEMPLATE
                        Template to use for intermediate CMake file
  --app-cmake-template APP_CMAKE_TEMPLATE
                        Template to use for application CMake file
  --lib-cmake-template LIB_CMAKE_TEMPLATE
                        Template to use for library CMake file
                        ```
