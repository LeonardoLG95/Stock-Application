# Stock looker

An application to follow the stocks of the companies 
that are part of the SP500, Nasdaq100 and DOW.
Also, you will be able to follow your portfolio 
(not yet).


### Pre-requisites 📋

To use this application you need to have Docker 
installed and know the basics.


### Installation 🔧

Use docker build for the Django and service(not yet) 
images in docker folder.

You will have to migrate the Django models 
to your database and you will have to add 
insert_date default = now () and not null = False 
manually since Django handles the default values 
itself, it does not pass the rule to the database 
and this is required by the service.


#README NOT FINISHED (SAME AS THE PROJECT)
