cmake_minimum_required(VERSION 3.5)

project(NetSpeed LANGUAGES CXX)

set(CMAKE_INCLUDE_CURRENT_DIR ON)

set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt5 COMPONENTS Widgets REQUIRED)

add_executable(NetSpeed
  main.cpp
  mainwindow.cpp
  mainwindow.h
)

target_link_libraries(NetSpeed PRIVATE Qt5::Widgets)
