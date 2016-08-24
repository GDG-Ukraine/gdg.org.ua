# -*- mode: ruby -*-
# vi: set ft=ruby ts=2 sw=2 sts=2 et :


$script = <<SCRIPT
VAGGA_CONF_FILE='/home/vagrant/.vagga/settings.yaml'
if ! grep -q "ubuntu-mirror: " $VAGGA_CONF_FILE
then
    echo "Ubuntu mirror config not found in vagga settings. Appending..."
    echo "ubuntu-mirror: http://ua.archive.ubuntu.com/" >> $VAGGA_CONF_FILE
else
    echo "Ubuntu mirror config was found. Leaving as is"
fi;
SCRIPT


unless Vagrant.has_plugin?("vagrant-vagga")
  abort 'vagrant-vagga plugin is not installed! Do first # vagrant plugin install vagrant-vagga'
end


Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/trusty64"

  config.vm.provision "setup-vagga", type: "vagga"
  config.vm.provision "config-vagga", type: "shell", inline: $script

  config.vm.network :forwarded_port, guest: 8080, host: 8080, auto_correct: false

  config.vm.box_check_update = false

  config.vm.provider "virtualbox" do |vbox|
    vbox.name = "gdg.org.ua"
  end
end
