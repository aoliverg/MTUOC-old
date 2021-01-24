# MTUOC

MTUOC is a project from the Universitat Oberta de Catalunya (UOC) wit the goal of making the integration of neural (and statistical) machine translation in professional translation environments easier. The project includes the following components:

* Basic processing components developed in Python.
** Tokenizers.
** Truecaser (both a program to train truecaser models and the truecaser itself).
** Basic replacement and restoring modules for URLs and Emails.
** Basic scripts for replacing and restoring numerical expressions.
* Python scripts for converting TMX files to tab delimited files.
* Corpus preparation scripts.
- Scripts for preprocessing parallel corpora to be used in training neural of statistical MT systems.
- Configuration scripts for training using several MT toolkits (Marian, OpenNMT, Moses and other to be defined).
- An MT server able to connect with the most popular MT toolkits (Marian, OpenNMT, ModernMT, Moses and other to be defined). This server is able to behave as different servers (OpenNMT, NMTWizard, ModernMT, Moses and other to be defined) with the aim to be compatible with a high number of CAT tools).
- A simple client for testing and evaluation purposes. This component is host in another repository (https://github.com/aoliverg/MTUOC-translator)
- A VirtuaBox virtual machine configured and ready to run the server.
- ([to be developed) Docker and Nvidia-docker versions of the server.)

