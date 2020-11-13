# MTUOC

MTUOC is a project from the Universitat Oberta de Catalunya (UOC) wit the goal of making the integration of neural (and statistical) machine translation in professional translation environments easier. The project includes the following components:

- Scripts and programs for preprocessing parallel corpora to be used in training neural of statistical MT systems.
- Configuration scripts for training using several MT toolkits (Marian, OpenNMT, Moses and other to be defined).
- An MT server able to connect with the most popular MT toolkits (Marian, OpenNMT, ModernMT, Moses and other to be defined). This server is able to behave as different servers (OpenNMT, NMTWizard, ModernMT, Moses and other to be defined) with the aim to be compatible with a high number of CAT tools). This component is host in another repository (https://github.com/aoliverg/MTUOC-server)
- A simple client for testing and evaluation purposes. This component is host in another repository (https://github.com/aoliverg/MTUOC-translator)
- ([to be developed] A web interface for translating text and documents using a running server.)
- A VirtuaBox virtual machine configured and ready to run the server.
- ([to be developed) Docker and Nvidia-docker versions of the server.)

