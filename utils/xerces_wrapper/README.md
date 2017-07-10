# The Xerces Wrapper

In the context of the Curator, XML files are handled using the LXML library. When it comes to XML validation, LXML is able to support most of the XML specification, but not all of it.
We encountered some limitations using the LXML library. Here are some examples that will be incorrectly declared invalid by LXML:
- Instantiate an XML document having the root using xsi:type,
	- Problem: LXML only supports XML documents with a root element,
- Make use of the XML standard 1.1
	- Problem: LXML only supports XML standard 1.0

We looked at other solutions and decided to integrate the Xerces library to the Curator for the validation of XML Schemas and XML documents.
Here are some reasons why we chose to use the Xerces library:
- It is listed in w3 tools (https://www.w3.org/XML/Schema.html#Tools)
- It is part of the Apache Software Foundation
- It is used by the popular Oxygen XML editor.

**From the LXML documentation:**
-	Supported XML standards: XML 1.0, XML Schema 1.0.
-	Support for XML Schema is currently not 100% complete in libxml2, but is definitely very close to compliance.
source: http://lxml.de/FAQ.html#what-standards-does-lxml-implement

**From the Xerces-C documentation:**
-	Supported XML standards: XML 1.0, XML 1.1, XML Schema 1.0, XML Schema 1.1 (Working Drafts, December 2009)
-	Xerces2 is a fully conforming XML Schema 1.0 processor. A partial experimental implementation of the XML Schema 1.1...
sources: http://xerces.apache.org/ http://xerces.apache.org/xerces2-j/


There are several implementations of Xerces in different languages (Java, C++, Perl), but there is currently no python implementation.
In most cases, it won't be necessary to use Xerces, but to allow users to validate any kind of XML schemas and XML documents we have implemented a python wrapper to the Xerces-C library.
To do so, we developed our own C++ API using the Xerces-C library and built.
To avoid building a wrapper for the entire Xerces-C library, the C++ API has been built using only a subset of the library.
The C++ API is defining two main methods to validate an XML schema and an XML document. 
To make this API available to the Curator, a python wrapper has been generated on top of the API. The python wrapper is generated using SWIG. 

The two methods that can be used via the Xerces Wrapper are:

 **validate_xsd(xsd_string)**: Checks if the XML Schema is well formed
```
params:	
	xsd_string: String containing the XML Schema (XSD file)
return: 
	errors: String containing a list of errors encountered during the validation of the XML Schema
```

**validate_xml(xsd_string, xml_string)**: Checks if the XML document is well formed and valid for the XML Schema
```
params:	
	xsd_string: String containing the XML Schema (XSD file)
	xml_string: String containing the XML Document (XML file)
return: 
	errors: String containing a list of errors encountered during the validation of the XML Document		
```		
		
The methods can be called from a python program using:
```
import xerces_wrapper
errors = xerces_wrapper.validate_xsd(xsd_string)
errors = xerces_wrapper.validate_xml(xsd_string, xml_string)
```

**Sources:**
- Xerces-C: https://xerces.apache.org/xerces-c/
- SWIG: http://www.swig.org/


## Installation

Please follow these instructions to install the Xerces Wrapper for validation.
If the installation succeeds, you will have fully compliant validation, otherwise, the Curator will continue using the LXML library.

# Linux

**Prerequisites**

- Install GNU GCC Compiler: 
```
qpt-get install build-essential
```
- Install SWIG: 
```
apt-get install swig
```
- Download Xerces-C (http://xerces.apache.org/xerces-c/download.cgi):
```bash
wget <mirror_address> #e.g. wget http://apache.mesi.com.ar//xerces/c/3/sources/xerces-c-3.1.3.tar.gz)
tar -zxvf xerces-c-<version>.tar.gz (e.g. tar -zxvf xerces-c-3.1.3.tar.gz)
cd xerces-c-<version>
./configure
make install
ldconfig
```

- Open setup.py:
	- In library_dirs and include_dirs, write the path to xerces-c/src (e.g. /home/user/xerces-c/src)
- Install the Xerces Wrapper:
```
python setup.py install 
```
- Test if the package is successfully installed:
```
python -c "import xerces_wrapper"
```
	
If the import is returning errors, it may mean that the package has not been installed at the correct location. 
For more information about the installation location, please read: https://docs.python.org/2/install#how-installation-works

**Note:** The following command will tell you where your current python is looking for packages:
```
python -c "import site; print site.getsitepackages()"
```
**Note:** If no succes with auto install, you can directly copy and paste the file xerces_wrapper.pyc and _xerces_wrapper.so into the site-packages folder of your python.


# MacOS

**Prerequisites**

- Install PCRE (https://sourceforge.net/projects/pcre/files/):
```
./configure
make 
sudo make install
```
- Install SWIG (http://www.swig.org/download.html):
```
./configure
make 
sudo make install
```
- Download Xerces-C (http://xerces.apache.org/xerces-c/download.cgi):
```bash
tar -zxvf xerces-c-<version>.tar.gz #(e.g. tar -zxvf xerces-c-3.1.3.tar.gz)
cd xerces-c-<version>
./configure --enable-netaccessor-curl CFLAGS="-arch x86_64" CXXFLAGS="-arch x86_64" 
sudo make install
```

- Open setup.py:
	- In library_dirs and include_dirs, write the path to xerces-c/src (e.g. /home/user/xerces-c/src)
- Install the Xerces Wrapper:
```
python setup.py install 
```
- Test if the package is successfully installed:
```
python -c "import xerces_wrapper"
```

If the import is returning errors, it may mean that the package has not been installed at the correct location. 
For more information about the installation location, please read: https://docs.python.org/2/install#how-installation-works

**Note:** The following command will tell you where your current python is looking for packages:
```
python -c "import site; print site.getsitepackages()"
```
**Note:** If no success with auto install, you can directly copy and paste the file xerces_wrapper.pyc and _xerces_wrapper.so into the site-packages folder of your python.

## Enable Xerces in the MDCS

Please follow the following instructions to enable Xerces validation in the MDCS:
- Install PyZMQ:
```
pip install pyzmq
```
- Open mgi/settings.py, and set:
```
XERCES_VALIDATION = True
```
- Run:
```
python utils/XMLValidation/xerces_server.py
```

