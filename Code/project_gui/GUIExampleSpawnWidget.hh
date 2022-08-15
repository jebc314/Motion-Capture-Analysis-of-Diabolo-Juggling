/*
 * Copyright (C) 2014 Open Source Robotics Foundation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
*/
#ifndef _GUI_EXAMPLE_SPAWN_WIDGET_HH_
#define _GUI_EXAMPLE_SPAWN_WIDGET_HH_

#include <gazebo/common/Plugin.hh>
#include <gazebo/gui/GuiPlugin.hh>
#include <string>
#include <vector>
#include <map>

// moc parsing error of tbb headers
#ifndef Q_MOC_RUN
#include <gazebo/transport/transport.hh>
#endif

namespace gazebo
{
    class GAZEBO_VISIBLE GUIExampleSpawnWidget : public GUIPlugin
    {
      Q_OBJECT

      /// \brief Constructor
      /// \param[in] _parent Parent widget
      public: GUIExampleSpawnWidget();

      /// \brief Destructor
      public: virtual ~GUIExampleSpawnWidget();

      /// \brief Callback trigged when the button is pressed.
      protected slots: void OnButtonPressed();
      /// \brief Callback trigged when the button is released.
      protected slots: void OnButtonReleased();
      
      /// \brief Callback trigged when want to save data.
      protected slots: void OnSave();

      /// \brief Override the Load function
      //public slots: void Load(sdf::ElementPtr /*_sdf*/);

      /// \brief Counter used to create unique model names
      private: unsigned int counter;

      /// \brief Keeps track of what models are displayed
      private: std::vector<std::string> currentModels;

      /// \brief Descriptions for each of the moves
      private: std::map<std::string, std::string> *movesDescription;

      /// \brief QLabel that holds the descriptions
      private: QLabel *label;
      
      /// \brief Current move name 
      private: std::string currentMove;

      /// \brief Node used to establish communication with gzserver.
      private: transport::NodePtr node;

      /// \brief Publisher of factory messages.
      private: transport::PublisherPtr factoryPub;
    };
}
#endif
