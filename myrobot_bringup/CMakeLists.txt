cmake_minimum_required(VERSION 3.8)
project(myrobot_bringup)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)

# Installation de TOUS les dossiers de configuration et ressources
install(
  DIRECTORY config launch rviz worlds
  DESTINATION share/${PROJECT_NAME}
)

# ⚠️ Toujours en DERNIER ! C'est cette fonction qui clôture le package ROS 2
ament_package()