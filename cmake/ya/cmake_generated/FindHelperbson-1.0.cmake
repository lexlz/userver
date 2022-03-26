# AUTOGENERATED, DON'T CHANGE THIS FILE!

if (NOT bson-1.0_FIND_VERSION OR bson-1.0_FIND_VERSION VERSION_LESS 1.16.0)
    set(bson-1.0_FIND_VERSION 1.16.0)
endif()

if (NOT USERVER_CHECK_PACKAGE_VERSIONS)
  unset(bson-1.0_FIND_VERSION)
endif()

if (TARGET bson-1.0)
  if (NOT bson-1.0_FIND_VERSION)
      set(bson-1.0_FOUND ON)
      return()
  endif()

  if (bson-1.0_VERSION)
      if (bson-1.0_FIND_VERSION VERSION_LESS_EQUAL bson-1.0_VERSION)
          set(bson-1.0_FOUND ON)
          return()
      else()
          message(FATAL_ERROR
              "Already using version ${bson-1.0_VERSION} "
              "of bson-1.0 when version ${bson-1.0_FIND_VERSION} "
              "was requested."
          )
      endif()
  endif()
endif()

set(FULL_ERROR_MESSAGE "Could not find `bson-1.0` package.\n\tDebian: sudo apt update && sudo apt install libyandex-taxi-mongo-c-driver-dev\n\tMacOS: brew install yandex-taxi-mongo-c-driver")


include(FindPackageHandleStandardArgs)





if (bson-1.0_VERSION)
  set(bson-1.0_VERSION ${bson-1.0_VERSION})
endif()

if (bson-1.0_FIND_VERSION AND NOT bson-1.0_VERSION)
  include(DetectVersion)

  if (UNIX AND NOT APPLE)
    deb_version(bson-1.0_VERSION libyandex-taxi-mongo-c-driver-dev)
  endif()
  if (APPLE)
    brew_version(bson-1.0_VERSION yandex-taxi-mongo-c-driver)
  endif()
endif()

find_package(bson-1.0 1.16.0
 )
set(bson-1.0_FOUND ${bson-1.0_FOUND})
 

if (NOT bson-1.0_FOUND)
  if (bson-1.0_FIND_REQUIRED)
      message(FATAL_ERROR "${FULL_ERROR_MESSAGE}. Required version is at least ${bson-1.0_FIND_VERSION}")
  endif()

  return()
endif()

if (bson-1.0_FIND_VERSION)
  if (bson-1.0_VERSION VERSION_LESS bson-1.0_FIND_VERSION)
      message(STATUS
          "Version of bson-1.0 is '${bson-1.0_VERSION}'. "
          "Required version is at least '${bson-1.0_FIND_VERSION}'. "
          "Ignoring found bson-1.0."
          "Note: Set -DUSERVER_CHECK_PACKAGE_VERSIONS=0 to skip package version checks if the package is fine."
      )
      set(bson-1.0_FOUND OFF)
      return()
  endif()
endif()

 
if (NOT TARGET bson-1.0)
  add_library(bson-1.0 INTERFACE IMPORTED GLOBAL)

  target_include_directories(bson-1.0 INTERFACE ${bson-1.0_INCLUDE_DIRS})
  target_link_libraries(bson-1.0 INTERFACE ${bson-1.0_LIBRARIES})
  
  # Target bson-1.0 is created
endif()

if (bson-1.0_VERSION)
  set(bson-1.0_VERSION "${bson-1.0_VERSION}" CACHE STRING "Version of the bson-1.0")
endif()