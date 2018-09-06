Samanta
=======
A Simple Account Management for Tools and Applications. It includes the basic functionalities for users:

  * Register
  * Profile
  * Password recovery

This package is under development, therefore just the branch Dev is currently existing.

Installation
============
Since the app is not yet ready and exist just in this repository, there are few methods to install it. First you need to download it and use one of the following options to install. Let say you download it in a zip file with the name samanta.zip.

First option:

1. ``pip install samanta.zip``
2. Add ``samanta`` and its dependencies to the to ``INSTALLED_APPS``
  What are the dependencies? 'django-simple-captcha' (include as 'captcha') and 'django-countries'

Second option:

1.  Decompress the downloaded file, you will see the same files you see in Github/Bitbucket. Here you have several options for installation. Since we are under development, I suggest the following:
2. ``python setup.py develop``
3. Add ``samanta`` and its dependencies to the to ``INSTALLED_APPS``
  What are the dependencies? 'django-simple-captcha' (include as 'captcha') and 'django-countries'

This will allow you to have the package installed in development mode.

Features
========
The features in Samanta are very simple and are the basics that will be used in all my web apps in the future:

* Profile: Very basic user profile with fields like regarding personal data. All this values are optional and will be saved just if the user wants to save them. since they will be public inside the tool. Just registered and active used will be able to see them. The idea is to use this data for some statistics. 

    * Date of birth
    * Location: Country
    * Language 
    * Gender
    * Avatar
    * Unban time: to ban users until a certain date. Checked at login time.
    * Teams: Equivalent to Groups, but without special permissions

* Views:
    * Profile: A simple user profile where they can se their own data and edit it. Up to now the public version is not yet ready. It is in the private-experimental-branches.
    * Register: Set of views to users to register themselves. It is based in an email confirmation and all data is stored in the conjunction with a log. Samanta does not use the normal session stored data from Django, since the idea is to have registers of what is going on.
    * Email change: Basic option to change emails. It also works based on email confirmations and logs.
    * Password change and recovery: Same idea than for email change.

* Email integration:
    All the views related with user creation, password and email changes require email confirmation by the users to take efect. 


Further options
===============
Just for Linux.

If you look at the source of the file, you will notice that there is a makefile inside. You can use it in order to perform some operations
to use it you need to be in the same file than the makefile. The commands are very simple.

``make <option>``

With the optionc:

* ``clean-pyc``: Removes all python compiled files (pyc) 
* ``test``: Run unit tests and doctests for the complete package.
* ``document``: Runs sphinx to generate the documentation. It can be found afterwards in the folder 'docs\build\html'
* ``install``: Installs the package using pip
* ``install-devel``: Install the package using python in development mode

