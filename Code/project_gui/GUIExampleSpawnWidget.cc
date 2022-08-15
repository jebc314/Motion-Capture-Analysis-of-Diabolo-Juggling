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
#include <sstream>
#include <gazebo/msgs/msgs.hh>
#include "GUIExampleSpawnWidget.hh"
#include <iostream>
#include <functional>
#include <gazebo/common/common.hh>
#include <gazebo/physics/physics.hh>
#include <gazebo/util/IntrospectionManager.hh>
#include <sdf/sdf.hh>
#include <string>
//#include <ignition/math/Pose3.hh>
#include <fstream>

using namespace gazebo;

// Register this plugin with the simulator
GZ_REGISTER_GUI_PLUGIN(GUIExampleSpawnWidget)

/////////////////////////////////////////////////
GUIExampleSpawnWidget::GUIExampleSpawnWidget()
  : GUIPlugin()
{
  std::cout << "Ran GUI Constructor" << std::endl;
  this->counter = 0;

  // Set the frame background and foreground colors
  this->setStyleSheet(
      "QFrame { background-color : rgba(100, 100, 100, 255); color : white; }");

  // Create the main layout
  QGridLayout *mainLayout = new QGridLayout;

  /*
  // Test grid of mainlayout
  QLabel *test = new QLabel(tr("test"));
  mainLayout->addWidget(test, 0, 1);

  QLabel *test1 = new QLabel(tr("test test"));
  mainLayout->addWidget(test1, 1, 0, 1, 2);
  */

  // Create the frame to hold all the widgets
  QFrame *mainFrame = new QFrame();

  // Create the layout that sits inside the frame
  QVBoxLayout *frameLayout = new QVBoxLayout();

  // Create a push button, and connect it to the OnButton function
  // QPushButton *button = new QPushButton(tr("Spawn Sphere"));
  // connect(button, SIGNAL(clicked()), this, SLOT(OnButton()));

  // Add the button to the frame's layout
  // frameLayout->addWidget(button);
  
  /*** Jeb's Project ***/
  
  // list of buttons
  int num_buttons = 3;
  const char *button_labels[3] = {
     "Move 1",
     "Move 2",
     "Move 3"
  };
  
  QGroupBox *buttonGroup = new QGroupBox(tr("Switch Moves"));
  QVBoxLayout *vbox = new QVBoxLayout();
  
  for (int i = 0; i < num_buttons; i++) {
     QPushButton *move_button = new QPushButton(tr(button_labels[i]));
     // Add button function
     connect(move_button, SIGNAL(pressed()), this, SLOT(OnButtonPressed()));
     connect(move_button, SIGNAL(released()), this, SLOT(OnButtonReleased()));
     vbox->addWidget(move_button);
     // std::cout << button_labels[i];
  }
  vbox->addStretch(1);
  vbox->setContentsMargins(0, 0, 0, 0);
  buttonGroup->setLayout(vbox);
  
  frameLayout->addWidget(buttonGroup);
  
  /****/

  // Add frameLayout to the frame
  mainFrame->setLayout(frameLayout);

  // Add the frame to the main layout
  mainLayout->addWidget(mainFrame, 0, 0);

  // Remove margins to reduce space
  frameLayout->setContentsMargins(0, 0, 0, 0);
  mainLayout->setContentsMargins(0, 0, 0, 0);

  this->setLayout(mainLayout);

  // Position and resize this widget
  this->move(10, 10);
  this->resize(250, 750);


  // Create a node for transportation
  
  this->node = transport::NodePtr(new transport::Node());
  this->node->Init();
  this->factoryPub = this->node->Advertise<msgs::Factory>("~/factory");
  

   // Add Description Box
  QFrame *descriptionFrame = new QFrame();
  QVBoxLayout *descriptionLayout = new QVBoxLayout();

  QGroupBox *descriptionGroup = new QGroupBox(tr("Description"));
  QVBoxLayout *textVbox = new QVBoxLayout();
  this->label = new QLabel(tr("testing"));
  textVbox->addWidget(this->label);
  textVbox->setContentsMargins(0, 0, 0, 0);
  textVbox->addStretch(1);
  descriptionGroup->setLayout(textVbox);
  descriptionLayout->addWidget(descriptionGroup);
  
  QPushButton *downloadButton = new QPushButton(tr("Download Data"));
  connect(downloadButton, SIGNAL(clicked()), this, SLOT(OnSave()));
  descriptionLayout->addWidget(downloadButton);
  
  descriptionFrame->setLayout(descriptionLayout);
  mainLayout->addWidget(descriptionFrame, 1, 0);

  // Set ratio of row sizes
  mainLayout->setRowStretch(1, 20);

/*
  this->movesDescription.insert(pair<std::string, std::string>("Move 1", "These two long cylinders represent the sticks used in diabolo play."));
  this->movesDescription.insert(pair<std::string, std::string>("Move 2", "These two disks represent the sides of a diabolo rotating around the z-axis."));
  this->movesDescription.insert(pair<std::string, std::string>("Move 3", "This is the combination of moves 1 and 2."));
*/
}

//void GUIExampleSpawnWidget::Load(sdf::ElementPtr /*_sdf*/) 
/*{
  this->currentMove = "Move 1";
  
   // Introspection callback.
      auto fMoveValue = [this]()
      {
        return this->currentMove;
      };

   // Register the counter element.
   gazebo::util::IntrospectionManager::Instance()->Register<std::string>("data://my_plugin/move", fMoveValue);
}*/

/////////////////////////////////////////////////
GUIExampleSpawnWidget::~GUIExampleSpawnWidget()
{
}

/////////////////////////////////////////////////

void GUIExampleSpawnWidget::OnButtonPressed()
{
  QPushButton* buttonSender = qobject_cast<QPushButton*>(sender());
  QString buttonName = buttonSender->text();
  std::string buttonString = buttonName.toStdString();
  std::cout << buttonString << " Pressed" << std::endl;
  this->currentMove = buttonString;

  for (int i = 0; i < this->currentModels.size(); i++) {
    std::string currentModel = this->currentModels.at(i);
    transport::NodePtr node = boost::make_shared<transport::Node>();
    node->Init();
    transport::PublisherPtr request_pub = node->Advertise<msgs::Request>("~/request");
    msgs::Request *msg = msgs::CreateRequest("entity_delete", currentModel);
    request_pub->Publish(*msg);
    delete msg;
  }

}

void GUIExampleSpawnWidget::OnButtonReleased()
{
  QPushButton* buttonSender = qobject_cast<QPushButton*>(sender());
  QString buttonName = buttonSender->text();
  std::string buttonString = buttonName.toStdString();
  std::cout << buttonString << " Released" << std::endl;
  this->currentMove = buttonString;

  if (buttonString.compare("Move 1") == 0) {
    msgs::Factory msg;
    // Model file to load
    msg.set_sdf_filename("model://stick_pos");
    this->currentModels.push_back("stick_pos");
    this->factoryPub->Publish(msg);

    msgs::Factory msg1;
    msg1.set_sdf_filename("model://stick_neg");
    this->currentModels.push_back("stick_neg");
    this->factoryPub->Publish(msg1);

    //const auto *tempString = this->movesDescription->find("Move 1")->second;
    const std::string tempString = "These two long cylinders represent the sticks used in diabolo play.";
    this->label->setText(tr("These two long cylinders \nrepresent the sticks \nused in diabolo play."));
  } else if (buttonString.compare("Move 2") == 0){
    msgs::Factory msg;
    // Model file to load
    msg.set_sdf_filename("model://side_pos");
    this->currentModels.push_back("side_pos");
    this->factoryPub->Publish(msg);

    msgs::Factory msg1;
    msg1.set_sdf_filename("model://side_neg");
    this->currentModels.push_back("side_neg");
    this->factoryPub->Publish(msg1);

    //const auto *tempString = this->movesDescription->find("Move 2")->second;
    const std::string tempString = "These two disks represent the sides of a diabolo rotating around the z-axis.";
    this->label->setText(tr("These two disks represent \nthe sides of a diabolo \nrotating around the z-axis."));
  } else {
    msgs::Factory msg;
    // Model file to load
    msg.set_sdf_filename("model://stick_pos");
    this->currentModels.push_back("stick_pos");
    this->factoryPub->Publish(msg);

    msgs::Factory msg1;
    msg1.set_sdf_filename("model://stick_neg");
    this->currentModels.push_back("stick_neg");
    this->factoryPub->Publish(msg1);

    msgs::Factory msg2;
    // Model file to load
    msg2.set_sdf_filename("model://side_pos");
    this->currentModels.push_back("side_pos");
    this->factoryPub->Publish(msg2);

    msgs::Factory msg3;
    msg3.set_sdf_filename("model://side_neg");
    this->currentModels.push_back("side_neg");
    this->factoryPub->Publish(msg3);

    //const auto *tempString = this->movesDescription->find("Move 3")->second;
    const std::string tempString = "This is the combination of moves 1 and 2.";
    this->label->setText(tr("This is the combination \nof moves 1 and 2."));
  }
}

void GUIExampleSpawnWidget::OnSave()
{
  std::cout << "Saving" << std::endl;
  std::ofstream myfile;
  myfile.open("DIABOLO_DATA.txt");
  myfile << this->currentMove << std::endl;
  myfile.close();
}