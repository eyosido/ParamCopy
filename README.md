# ParamCopy
ParamCopy is a plugin for Substance 3D Designer enabling to perform various operations related to node parameters such as copy/paste and node state storing/recalling.

# Use case examples
- Copy common node Base parameters such as resolution or bit-depth from one node into multiple other nodes.
- Copy specific node parameters into other nodes of the same type, i.e. to uniformize a distribution, layout or processing between multiple nodes.
- Change the inheritance methods of some parameters by changing them into a source node and pasting into other nodes.
- Using named clipboards, create and name multiple node configurations that can be pasted into other nodes.
- Create multiple variations of a selected set of nodes then switch between them for testing different design options. Combine variations with those of other node sets and recall them all at once.
- Create and combine variations for development, testing or demonstration purpose, skim with a few clicks through variations showing multiple states of your Substance and even combine them.
- Copy/paste parameters between custom or third-party Substances of different types but having similar parameters.
- Shuffle the randomness of parts your graph by rolling the random seeds of a selection of nodes.

# Features
- Selective copy of node parameters into an internal clipboard and selective paste (including inheritance methods) into other nodes of same or other type. By default, both Base and Specific parameters are pasted into nodes of the same type as the source node, and only Base parameters pasted into nodes of different types. An option however enables to copy matching Specific parameters into nodes of different types, which can be used for node types having similar Specific parameters.
- Named clipboards enable handling of multiple clipboards created during parameter copy. Users can select one of these clipboards and paste it into the current node selection or make it current to paste it later.
- Non-persistent storage of variations composed of a set of node states with the ability to later recall stored variations. This enables to select a set of nodes involved into a design variation, store their state and this way switch between different variations with a few clicks, for development or demonstration purpose.
- Rolling of random seed Base parameters (i.e. random seeds are assigned to a random value) for a selection of nodes, so their randomness properties are being affected in a random manner. This enables to shuffle multiple nodes at a time to produce new outcomes.

# Requirements
ParamCopy 1.1.2 requires usage of Substance 3D Designer 12.1 or above.

# Installation
- In Substance 3D Designer, open the Plugin Manager (“Tools / Plugin Manager...” menu)
- Click the "INSTALL..." button and select the .sdplugin file.

The plugin will be installed on your user space (on Windows this is (user home)\Documents\Adobe\Adobe Substance 3D Designer\python\sduserplugins) and enabled in the Plugin Manager. You may disable/enable it in the Plugin Manager at any time.

The plugin creates a ParamCopy menu in the application’s top menu as well as a toolbar in newly created/opened graph.

# Upgrade
If upgrading from a previous version of the plugin, the latter must first be deleted from the user space, on Windows this is:

    <user home>\Documents\Adobe\Adobe Substance 3D Designer\python\sduserplugins
Then, launch Substance 3D Designer to install the new version of the plugin as mentioned above.

# Package download
Ready-to-use packages are available in the [releases folder](https://github.com/eyosido/ParamCopy/tree/main/releases).

# Documentation and tutorials
Documentation is part of the package download and also available in the [doc folder](https://github.com/eyosido/ParamCopy/tree/main/doc).

Tutorial videos up to version 1.1 are [available on Youtube](https://www.youtube.com/playlist?list=PLHiaUQJoD9AVxDR9W-Bg8LwQOfGUm5sTM).

# Build
To build the .sdplugin file from source, please follow the [procedure](https://substance3d.adobe.com/documentation/sddoc/packaging-plugins-182257149.html) mentioned in the Substance 3D Designer documentation.
