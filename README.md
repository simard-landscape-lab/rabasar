# Rabasar 

This is a python implementation of Ratio-Based Multitemporal SAR Images Denoising from the [RABASAR](https://hal.archives-ouvertes.fr/hal-01791355/) paper. RABASAR is application of the so-called [plug-and-play denoisers](https://arxiv.org/abs/1605.01710) for SAR image de-speckling to a temporal stack of intensity images. 

# Installation

The installations are based on python 3.7+ using anaconda and conda within a virtual environment. Generally, this is accomplished as follows:

1. Create a virtual environment using the `requirements.txt`
2. Install rabasar downloading this repo and `pip install .`

More explicitly, using the anaconda distribution for Mac or Windows:

1. `conda create --name rabasar_env python=3.7`
2. `conda activate rabasar_env`
3. `conda install -c conda-forge --yes --file requirements.txt`
4. `pip install .` (maybe at some point, we can distribute on pypi)
5. Ensure your python can be found by jupyter via `python -m ipykernel install --user`

You can make sure your installation was done correctly running `python -c "import rabasar"` and/or running the notebooks.

# References

### Rabasar
+ Zhao, et al. [RABASAR](https://hal.archives-ouvertes.fr/hal-01791355/), 2019.
+ Zhao, et al. [Github Repo](https://github.com/WeiyingZhao/Multitemporal-SAR-image-denoising), 2019.

### Spatial Denoising
+  Bioucas-Dias and Figueiredo. [Multiplicative Noise Removal Using Variable
Splitting and Constrained Optimization](https://arxiv.org/pdf/0912.1845.pdf), 2010.
+ Delladelle, et al. [MuLoG: Multi-channel Logarithm with Gaussian denoising](https://arxiv.org/abs/1704.05335), 2017.

### ADMM

+ Boyd, et al. [Distributed Optimization and Statistical
Learning via the Alternating Direction
Method of Multipliers](https://web.stanford.edu/~boyd/papers/pdf/admm_distr_stats.pdf), 2010.
+ Chan, et al. [Plug-and-Play ADMM for Image Restoration: Fixed Point Convergence and Applications](https://arxiv.org/abs/1605.01710), 2016.