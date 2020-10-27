# Rabasar 

This is a python implementation of Ratio-Based Multitemporal SAR Images Denoising from the [RABASAR](https://hal.archives-ouvertes.fr/hal-01791355/) paper. RABASAR is application of the so-called [plug-and-play denoisers](https://arxiv.org/abs/1605.01710) for SAR image de-speckling to a temporal stack of intensity images. 

## Algorithm Description

We have a speckle backscatter intensity image $I_0$ and we want to find $R$ such that:

$$
R = \argmin_{I \in \mathbb R^{M \times N}} \mathcal{R}(I) + P(I | I_0).
$$
Above $\mathcal{R}:\mathbb R^{M \times N} \to \mathbb R$ is an image regularizer such as the [total-variation norm](https://en.wikipedia.org/wiki/Total_variation_denoising) $|I|_1$ or [BM3D](http://www.cs.tut.fi/~foi/GCF-BM3D/). The noise model $P(I | I_0)$ is the fully-developed speckle model (see this [paper](https://arxiv.org/abs/1704.05335) and references therein). This tool is then applied to:
+  "reference image" (called the super-image in the paper): the temporally averaged image from the intensity stack.
+  ratio of each intensity image and the reference image (using a slightly different noise model).

The final de-sepeckled image is then the (denoised ratio) $\times$ (the denoised reference image). Each denoising step is solved using the [Alternating Direction Method of Multipliers](https://web.stanford.edu/~boyd/papers/admm_distr_stats.html) (ADMM).

## References

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


