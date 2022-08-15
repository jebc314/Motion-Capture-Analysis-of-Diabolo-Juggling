#include <functional>
#include <gazebo/gazebo.hh>
#include <gazebo/physics/physics.hh>
#include <gazebo/common/common.hh>
#include <ignition/math/Vector3.hh>
#include <cmath>
#include <iostream>

namespace gazebo
{
  class ModelRevolveY : public ModelPlugin
  {
    public: const double PI = std::acos(-1);
    public: double model_t;

    public: ModelRevolveY() {
        // t for time
        this->model_t = 0.0;
    }

    public: void Load(physics::ModelPtr _parent, sdf::ElementPtr /*_sdf*/)
    {
      // Store the pointer to the model
      this->model = _parent;

      // Listen to the update event. This event is broadcast every
      // simulation iteration.
      this->updateConnection = event::Events::ConnectWorldUpdateBegin(
          std::bind(&ModelRevolveY::OnUpdate, this));
    }

    // Called by the world update start event
    public: void OnUpdate()
    {

        this->model_t += 0.0005;
        this->model_t = std::fmod(this->model_t, 2*this->PI);

        const ignition::math::Pose3d initial = this->model->InitialRelativePose();
        // std::cout<<initial<<std::endl;

        this->model->SetLinkWorldPose(ignition::math::Pose3d(
            ignition::math::Vector3d(2*std::cos(this->model_t), 0, (2*std::sin(this->model_t))),
            ignition::math::Quaterniond(1.57, 0, 0))+initial, "link_1");

      // Apply a small linear velocity to the model.
      //this->model->SetLinearVel(ignition::math::Vector3d(-std::sin(this->model_t), 0, std::cos(this->model_t)));
    }

    // Pointer to the model
    private: physics::ModelPtr model;

    // Pointer to the update event connection
    private: event::ConnectionPtr updateConnection;
  };

  // Register this plugin with the simulator
  GZ_REGISTER_MODEL_PLUGIN(ModelRevolveY)
}