## Running Cosmolike projects (Basic instructions) <a name="des_y3_running_cosmolike_projects"></a> 

From `Cocoa/Readme` instructions:

> [!Note]
> We provide several cosmolike projects that can be loaded and compiled using `setup_cocoa.sh` and `compile_cocoa.sh` scripts. To activate them, comment the following lines on `set_installation_options.sh` 
> 
>     [Adapted from Cocoa/set_installation_options.sh shell script]
>     (...)
>
>     # ------------------------------------------------------------------------------
>     # The keys below control which cosmolike projects will be installed and compiled
>     # ------------------------------------------------------------------------------
>     #export IGNORE_COSMOLIKE_LSST_Y1_CODE=1
>     (...)
>     export IGNORE_COSMOLIKE_DES_Y3_CODE=1
>
>     (...)
>     # ------------------------------------------------------------------------------
>     # Cosmolike projects below -------------------------------------------
>     # ------------------------------------------------------------------------------
>     (...)
>     export DES_Y3_URL="https://github.com/CosmoLike/cocoa_des_y3.git"
>     export DES_Y3_NAME="des_y3"
>     #Pin the project version with at most one of the keys below (COMMIT, BRANCH, or TAG).
>     #If more than one is set, COMMIT wins over BRANCH, and BRANCH wins over TAG.
>     #If none is set, Cocoa loads the latest commit on the repository default branch.
>     #export DES_Y3_GIT_BRANCH="main"
>     #export DES_Y3_GIT_COMMIT="abc"
>     export DES_Y3_GIT_TAG="v4.10.4"

> [!NOTE]
> In case users need to rerun `setup_cocoa.sh`, Cocoa will not download previously installed packages, cosmolike projects, or large datasets, unless the following keys are set on `set_installation_options.sh`
>
>     [Adapted from Cocoa/set_installation_options.sh shell script]
>     # ------------------------------------------------------------------------------
>     # OVERWRITE_EXISTING_XXX_CODE=1 -> setup_cocoa overwrites existing PACKAGES ----
>     # overwrite: delete the existing PACKAGE folder and install it again -----------
>     # redownload: delete the compressed file and download data again ---------------
>     # These keys are only relevant if you run setup_cocoa multiple times -----------
>     # ------------------------------------------------------------------------------
>     (...)
>     export OVERWRITE_EXISTING_ALL_PACKAGES=1    # except cosmolike projects
>     #export OVERWRITE_EXISTING_COSMOLIKE_CODE=1 # dangerous (possible loss of uncommitted work)
>                                                 # if unset, users must manually delete cosmolike projects
>     #export REDOWNLOAD_EXISTING_ALL_DATA=1      # warning: some data is many GB

> [!NOTE]
> If users want to recompile cosmolike, there is no need to rerun the Cocoa general scripts. Instead, run the following three commands:
>
>      source start_cocoa.sh
>
> and
> 
>      source ./installation_scripts/setup_cosmolike_projects.sh
>
> and
> 
>       source ./installation_scripts/compile_all_projects.sh
> 
> or (in case users just want to compile des_y3 project)
>
>       source ./projects/des_y3/scripts/compile_des_y3.sh

> [!TIP]
> Assuming Cocoa is installed on a local (not remote!) machine, type the command below after step 2️⃣ to run Jupyter Notebooks.
>
>     jupyter notebook --no-browser --port=8888
>
> The terminal will then show a message similar to the following template:
>
>     (...)
>     [... NotebookApp] Jupyter Notebook 6.1.1 is running at:
>     [... NotebookApp] http://f0a13949f6b5:8888/?token=XXX
>     [... NotebookApp] or http://127.0.0.1:8888/?token=XXX
>     [... NotebookApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).
>
> Now go to the local internet browser and type `http://127.0.0.1:8888/?token=XXX`, where XXX is the previously saved token displayed on the line
> 
>     [... NotebookApp] or http://127.0.0.1:8888/?token=XXX
>
> The project des_y3 contains jupyter notebook examples located at `projects/des_y3`.


To run the example

**Step :one:**: activate the Cocoa Conda environment,  and the private Python environment 

      conda activate cocoa

and

      source start_cocoa.sh

**Step :two:**: Select the number of OpenMP cores (below, we set it to 8).

  - Linux
    
        export OMP_NUM_THREADS=8; export OMP_PROC_BIND=close; \
        export OMP_PLACES=cores; export OMP_DYNAMIC=FALSE; \
        export OPENBLAS_NUM_THREADS=1; export MKL_NUM_THREADS=1

  - macOS (arm)
    
        export OMP_NUM_THREADS=8; export OMP_PROC_BIND=disabled; \
        export OMP_PLACES=cores; export OMP_DYNAMIC=FALSE; \
        export OPENBLAS_NUM_THREADS=1; export MKL_NUM_THREADS=1


**Step :three:**: The folder `projects/des_y3` contains examples. So, run the `cobaya-run` on the first example following the commands below.

> [!Warning] 
> (Linux only) In some HPC nodes, `numa` can cause you problems. If that is the case,
> replace `numa` with `slot`

- **One model evaluation**:

  - Linux

        "${CONDA_PREFIX}"/bin/mpirun -n 1 --oversubscribe \
          --mca pml ob1 --mca btl vader,tcp,self \
          --bind-to core:overload-allowed --report-bindings \
          --rank-by slot --map-by numa:pe=${OMP_NUM_THREADS} \
          cobaya-run ./projects/des_y3/EXAMPLE_EVALUATE1.yaml -f

  - macOS (arm)

        mpirun -n 1 --oversubscribe \
         cobaya-run ./projects/des_y3/EXAMPLE_EVALUATE1.yaml -f

- **MCMC (Metropolis-Hastings Algorithm)**:

  - Linux

        "${CONDA_PREFIX}"/bin/mpirun -n 1 --oversubscribe \
          --mca pml ob1 --mca btl vader,tcp,self \
          --bind-to core:overload-allowed --report-bindings \
          --rank-by slot --map-by numa:pe=${OMP_NUM_THREADS} \
          cobaya-run ./projects/des_y3/EXAMPLE_MCMC1.yaml -f

  - macOS (arm)

        mpirun -n 4 --oversubscribe \
          cobaya-run ./projects/des_y3/EXAMPLE_MCMC1.yaml -f

# Baryonic feedback on EXAMPLE_EVALUATE1 <a name="des_y3_baryonic_feedback"></a>

`EXAMPLE_EVALUATE1.yaml` can apply an external baryonic feedback suppression to the
matter power spectrum via the `bfmt` theory block (SP(k), BCEmu, Flamingo, BACCOemu,
or BCemu2025). By default, the example runs without feedback.

**Step :one:**: ensure the lines below are commented out in `set_installation_options.sh`
before running `setup_cocoa.sh` and `compile_cocoa.sh`. *By default, these lines should
be commented out, but it is worth checking*.

      [Adapted from Cocoa/set_installation_options.sh shell script]
      #export IGNORE_PYSPK_CODE=1     # SP(k)
      #export IGNORE_BCEMU_CODE=1     # BCEmu
      #export IGNORE_FBRE_CODE=1      # FlamingoBaryonResponseEmulator
      #export IGNORE_BACCOEMU_CODE=1  # BACCOemu
      #export IGNORE_BFMT_CODE=1      # Baryon Feedback Theory Block

**Step :two:**: in `EXAMPLE_EVALUATE1.yaml`, uncomment the `bfmt` theory block and select
the model:

      theory:
        bfmt:
          baryon_model: 2 # 1 = SP(k), 2 = BCEmu, 3 = FlamingoEmulator, 4 = BACCOemu, 5 = BCemu2025

**Step :three:**: set `external_baryon_suppression: True` on the `des_y3.cosmic_shear`
likelihood block.

**Step :four:**: uncomment the selected model's parameters in the `params` block and in
the `sampler: evaluate: override` block (the example carries a commented block for each
model).

> [!TIP]
> For the sampled parameters of each model, their validity ranges, and the `bfmt`
> options, see `Cocoa/external_modules/code/baryon_suppression/README.md`.

# Running Hybrid Cosmolike-ML emulators <a name="cobaya_base_code_examples_emul2"></a>

> [!Warning]
> The code and examples associated with this section are still in alpha stage

Our main line of research involves emulators that simulate the entire Cosmolike data vectors, 
and each project (LSST, Roman, DES) contains its own README with emulator examples. 
The speed of such emulators is incredible, especially when GPUs are available, 
and our emulators do take advantage of the CPU-GPU integration on Apple MX chips.

While the data vector emulators are incredibly fast, there is an intermediate 
approach that emulates only the Boltzmann outputs (comoving distance, linear and 
nonlinear matter power spectrum). This hybrid-ML case can offer greater flexibility, 
especially in the initial phases of a research project, as changes to the modeling 
of nuisance parameters or to the assumed galaxy distributions do not require 
retraining of the network. 

Examples in the hybrid case all have the prefix **EXAMPLE_EMUL2** (note the `2`). The required flags on `set_installation_options.sh` are similar to what we showed in the previous emulator section.

Now, users must follow all the steps below.

 **Step :one:**: Activate the private Python environment by sourcing the script `start_cocoa.sh`

    source start_cocoa.sh

 **Step :two:**: Select the number of OpenMP cores. Below, we set it to 4, the ideal setting for hybrid examples.

  - Linux

        export OMP_NUM_THREADS=4; export OMP_PROC_BIND=close; \
        export OMP_PLACES=cores; export OMP_DYNAMIC=FALSE; \
        export OPENBLAS_NUM_THREADS=1; export MKL_NUM_THREADS=1

  - macOS (arm)
    
        export OMP_NUM_THREADS=4; export OMP_PROC_BIND=disabled; \
        export OMP_PLACES=cores; export OMP_DYNAMIC=FALSE; \
        export OPENBLAS_NUM_THREADS=1; export MKL_NUM_THREADS=1

 **Step :three:** Run `cobaya-run` on the first emulator example, following the commands below.

- **One model evaluation**:

  - Linux

        "${CONDA_PREFIX}"/bin/mpirun -n 1 --oversubscribe \
          --mca pml ob1 --mca btl vader,tcp,self \
          --bind-to core:overload-allowed --report-bindings \
          --rank-by slot --map-by numa:pe=${OMP_NUM_THREADS} \
          cobaya-run ./projects/des_y3/EXAMPLE_EMUL2_EVALUATE1.yaml -f

  - macOS (arm)
    
        mpirun -n 1 --oversubscribe \
          cobaya-run ./projects/des_y3/EXAMPLE_EMUL2_EVALUATE1.yaml -f
    
- **MCMC (Metropolis-Hastings Algorithm)**:

  - Linux

        "${CONDA_PREFIX}"/bin/mpirun -n 4 --oversubscribe \
          --mca pml ob1 --mca btl vader,tcp,self \
          --bind-to core:overload-allowed --report-bindings \
          --rank-by slot --map-by numa:pe=${OMP_NUM_THREADS} \
          cobaya-run ./projects/des_y3/EXAMPLE_EMUL2_MCMC1.yaml -r

  - macOS (arm)

        mpirun -n 4 --oversubscribe \
          cobaya-run ./projects/des_y3/EXAMPLE_EMUL2_MCMC1.yaml -r

> [!NOTE]
> **Running on more than one node.** The flag `--mca btl vader,tcp,self` works unchanged across
> nodes: Open MPI picks the transport per pair of ranks, using shared memory (`vader`) within a
> node and TCP between nodes. Three things deserve attention on multi-node runs:
>
> 1. **Network interface.** The TCP layer must not select an interface that is not routable
>    between compute nodes. The flag `--mca btl_tcp_if_exclude lo,docker0,virbr0,ib0` excludes
>    the common offenders. TCP bandwidth is not a limitation for our workloads, which exchange
>    small, infrequent MPI messages.
>
> 2. **Environment.** Ranks on remote nodes must see Cocoa's environment (`ROOTDIR`, `PATH`,
>    `LD_LIBRARY_PATH`, `PYTHONPATH`, `CONDA_PREFIX`, the OpenMP/BLAS thread settings, and
>    `CLIK_PATH`/`CLIK_DATA`/`CLIK_PLUGIN`). Slurm forwards the submitting environment
>    automatically; the explicit `-x` flags in our sbatch templates repeat this so the
>    scripts also work under ssh-based launchers. No other Cocoa installation flags are read at runtime.
>
> 3. **Slurm geometry.** Keep `ntasks-per-node` × `cpus-per-task` no larger than the cores per
>    node, and use `--map-by numa:pe=${OMP_NUM_THREADS}` so each rank reserves the cores its
>    OpenMP threads will use.

> [!NOTE]
> **Note on core oversubscription**: an MPI process that is waiting still burns 100% of its
> core, checking for messages in a loop. With more processes than cores, this stalls the
> processes doing real work. Open MPI usually detects this and makes waiting processes give
> up the CPU, but its detection can be fooled. Adding `--mca mpi_yield_when_idle 1` forces
> that behavior; it is harmless otherwise.

The `Nautilus`, `Minimizer`, `Profile`, and `Emcee` scripts below contain an internally 
defined `yaml_string` that specifies priors, 
likelihoods, and the theory code, all following Cobaya Conventions.

- **Nautilus**:

  - Linux 
    
        export OMP_NUM_THREADS=1

        "${CONDA_PREFIX}"/bin/mpirun -n 96 --oversubscribe --mca pml ob1 --mca btl vader,tcp,self \
          -x PATH -x LD_LIBRARY_PATH -x PYTHONPATH -x CONDA_PREFIX -x ROOTDIR \
          -x OMP_NUM_THREADS -x OMP_PROC_BIND -x OMP_PLACES -x OMP_DYNAMIC \
          -x OPENBLAS_NUM_THREADS -x MKL_NUM_THREADS -x CLIK_PATH -x CLIK_DATA \
          -x CLIK_PLUGIN --mca mpi_yield_when_idle 1 \
          --mca btl_tcp_if_exclude lo,docker0,virbr0,ib0 \
          --bind-to core:overload-allowed --report-bindings \
          --rank-by slot --map-by numa:pe=${OMP_NUM_THREADS} \
          python -m mpi4py.futures ./projects/des_y3/EXAMPLE_EMUL2_NAUTILUS1.py \
            --root ./projects/des_y3/ --outroot "EXAMPLE_EMUL2_NAUTILUS1"  \
            --maxfeval 750000 --nlive 2048 --neff 15000 \
            --flive 0.01 --nnetworks 5

  - macOS (arm)

        export OMP_NUM_THREADS=1

        mpirun -n 12 --oversubscribe \
          python -m mpi4py.futures ./projects/des_y3/EXAMPLE_EMUL2_NAUTILUS1.py \
            --root ./projects/des_y3/ \
            --outroot "EXAMPLE_EMUL2_NAUTILUS1" \
            --maxfeval 750000 --nlive 2048 --neff 15000 \
            --flive 0.01 --nnetworks 5

- **Global Minimizer**:

  Our minimizer is a reimplementation of `Procoli`, developed by Karwal et al (arXiv:2401.14225) 

  - Linux ($n_{\rm param} = 17$, assuming node with 96 cores)

        export OMP_NUM_THREADS=4

        "${CONDA_PREFIX}"/bin/mpirun -n 24 --oversubscribe --mca pml ob1 --mca btl vader,tcp,self \
          -x PATH -x LD_LIBRARY_PATH -x PYTHONPATH -x CONDA_PREFIX -x ROOTDIR \
          -x OMP_NUM_THREADS -x OMP_PROC_BIND -x OMP_PLACES -x OMP_DYNAMIC \
          -x OPENBLAS_NUM_THREADS -x MKL_NUM_THREADS -x CLIK_PATH -x CLIK_DATA \
          -x CLIK_PLUGIN --mca mpi_yield_when_idle 1 \
          --mca btl_tcp_if_exclude lo,docker0,virbr0,ib0 \
          --bind-to core:overload-allowed --report-bindings \
          --rank-by slot --map-by numa:pe=${OMP_NUM_THREADS} \
          python ./projects/des_y3/EXAMPLE_EMUL2_MINIMIZE1.py \
            --root ./projects/des_y3/ \
            --outroot "EXAMPLE_EMUL2_MIN1" \
            --nstw 350

  - macOS (arm)

        export OMP_NUM_THREADS=1

        mpirun -n 12 --oversubscribe \
          python ./projects/des_y3/EXAMPLE_EMUL2_MINIMIZE1.py \
            --root ./projects/des_y3/ \
            --outroot "EXAMPLE_EMUL2_MIN1" \
            --nstw 350
    
    
  The number of steps per Emcee walker per temperature is $n_{\rm stw}$,
  and the number of walkers is $n_{\rm w}={\rm max}(3n_{\rm params},n_{\rm MPI})$.
  The minimum number of total evaluations is $3n_{\rm params} \times n_{\rm T} \times n_{\rm stw}$, which can be distributed among $n_{\rm MPI} = 3n_{\rm params}$ MPI processes for faster results.

- **Profile**: 

  - Linux ($n_{\rm param} = 17$, assuming node with 96 cores)

        export OMP_NUM_THREADS=4

        "${CONDA_PREFIX}"/bin/mpirun -n 24 --oversubscribe --mca pml ob1 --mca btl vader,tcp,self \
          -x PATH -x LD_LIBRARY_PATH -x PYTHONPATH -x CONDA_PREFIX -x ROOTDIR \
          -x OMP_NUM_THREADS -x OMP_PROC_BIND -x OMP_PLACES -x OMP_DYNAMIC \
          -x OPENBLAS_NUM_THREADS -x MKL_NUM_THREADS -x CLIK_PATH -x CLIK_DATA \
          -x CLIK_PLUGIN --mca mpi_yield_when_idle 1 \
          --mca btl_tcp_if_exclude lo,docker0,virbr0,ib0 \
          --bind-to core:overload-allowed --report-bindings \
          --rank-by slot --map-by numa:pe=${OMP_NUM_THREADS} \
          python ./projects/des_y3/EXAMPLE_EMUL2_PROFILE1.py \
            --root ./projects/des_y3/ --cov 'chains/EXAMPLE_EMUL2_MCMC1.covmat' \
            --outroot "EXAMPLE_EMUL2_PROFILE1" \
            --factor 3 --nstw 350 --numpts 10 \
            --profile 1 \
            --minfile="./projects/des_y3/chains/EXAMPLE_EMUL2_MIN1.txt"

  - macOS (arm)
        
        export OMP_NUM_THREADS=1
        
        mpirun -n 12 --oversubscribe \
          python ./projects/des_y3/EXAMPLE_EMUL2_PROFILE1.py \
            --root ./projects/des_y3/ \
            --cov 'chains/EXAMPLE_EMUL2_MCMC1.covmat' \
            --outroot "EXAMPLE_EMUL2_PROFILE1" \
            --factor 3 --nstw 350 --numpts 10 --profile 1 \
            --minfile="./projects/des_y3/chains/EXAMPLE_EMUL2_MIN1.txt"

Details on the matter power spectrum emulator designs will be presented in the 
[emulator_code](https://github.com/SBU-COSMOLIKE/emulators_code) repository. 
Basically, we apply standard neural network techniques to generalize 
the *syren-new* Eq. 6 of [arXiv:2410.14623](https://arxiv.org/abs/2410.14623) 
formula for the linear power spectrum (w0waCDM with a fixed neutrino mass of $0.06$ eV) 
to new models, extended ranges, or higher precision. 
Similarly, we use networks to generalize the *syren-Halofit* LCDM nonlinear 
boost fit (Eq. 11 of [arXiv:2402.17492](https://arxiv.org/abs/2402.17492)).

# Unit tests <a name="des_y3_unit_tests"></a>

The `tests/` folder holds 24 pass/fail tests. They cover six
configurations: cosmic shear, 3x2pt, and 2x2pt, each evaluated on the
DES-Y3 covariance and n(z) and again on the DES-Y1 covariance and
n(z), with both the NLA and the TATT intrinsic-alignment models. Each
configuration gets one $\chi^2$ test against a stored reference and one
race check: ten cosmologies evaluated in a row on one model, with the
10th evaluation of the fiducial point required to reproduce a fresh
evaluation to $10^{-4}$. Every model build runs in its own worker
subprocess: the Y1 and Y3 data sets have different dimensions, and
cosmolike aborts a process that initializes both. Everything a test
evaluates is a frozen copy under `tests/frozen/`, pinned by a SHA-256
manifest, so edits to the live examples, the likelihood defaults, or
`data/` cannot reach the tests. To run the suite (from the `Cocoa/`
folder, cocoa environment active, `start_cocoa.sh` sourced):

    python -m pytest ./projects/des_y3/tests

[tests/README.md](tests/README.md) lists every test and the procedure
that refreshes the frozen state.

# Minimum accuracy parameters <a name="des_y3_minimum_accuracy"></a>

The advisory checks in `tests/test_accuracy.py` measure the numerical
error of the example defaults (`accuracyboost: 1.0`,
`integration_accuracy: 0`, `lmax: 50000`, `kmax_boltzmann: 5.0`, CAMB
`AccuracyBoost: 1.05`, `k_per_logint: 10`): each configuration is
re-evaluated at its reference point with every knob pushed far beyond
the defaults (cosmolike `accuracyboost: 3`, `integration_accuracy:
10`, ``lmax: 200000``, ``kmax_boltzmann: 40``; CAMB `AccuracyBoost: 2`,
`k_per_logint: 50`, `kmax: 50`), and the difference
`delta chi2 = chi2(high accuracy) - chi2(default)` is reported. The
target is `|delta chi2|` below 0.2, the bound the drift tests use.
Values measured at the freeze of 2026-09-21:

| check | configuration                        | $\Delta\chi^2$ |
|-------|--------------------------------------|-----------:|
| A1    | des_y3 cosmic shear (example1), NLA  |  -0.000029 |
| A2    | des_y3 cosmic shear (example1), TATT |  -0.000033 |
| A3    | des_y3 2x2pt (example2_2x2pt), NLA   |  +0.003159 |
| A4    | des_y3 2x2pt (example2_2x2pt), TATT  |  +0.003293 |
| A5    | des_y3 3x2pt (example2), NLA         |  +0.004083 |
| A6    | des_y3 3x2pt (example2), TATT        |  +0.004226 |
| A7    | des_y1 cosmic shear (example3), NLA  |  +0.000023 |
| A8    | des_y1 cosmic shear (example3), TATT |  +0.000023 |
| A9    | des_y1 2x2pt (example4_2x2pt), NLA   |  +0.001330 |
| A10   | des_y1 2x2pt (example4_2x2pt), TATT  |  +0.001326 |
| A11   | des_y1 3x2pt (example4), NLA         |  +0.001383 |
| A12   | des_y1 3x2pt (example4), TATT        |  +0.001380 |

One knob at a time on the des_y3 3x2pt (example2, NLA) configuration:

| knob                                     | $\Delta\chi^2$ |
|------------------------------------------|-----------:|
| `accuracyboost: 3`                       |  +0.000084 |
| `accuracyboost: 5` (stress)              |  +0.000535 |
| `integration_accuracy: 10`               |  +0.003724 |
| `lmax: 200000`                           |  +0.000087 |
| `kmax_boltzmann: 40` + CAMB `kmax: 50`   |  +0.000014 |
| CAMB `AccuracyBoost: 2`                  |  +0.000262 |
| CAMB `k_per_logint: 50`                  |  +0.000188 |

`accuracyboost` refines a nested z grid in the power-spectrum
tables: every coarser grid's nodes are a subset of every finer
grid's, so a higher boost tightens the same interpolation instead of
moving the nodes (the construction is commented in
`likelihood/_cosmolike_prototype_base.py`).

Every measured `|delta chi2|` is below 0.005, forty times smaller
than the 0.2 target, so the shipped des_y3 defaults are adequate for
both the DES-Y3 and the DES-Y1 data.

When a future change moves several knob deltas at once, raise the
cosmolike `accuracyboost` first (cheap at run time), then CAMB
`k_per_logint`, and only then CAMB `AccuracyBoost` (expensive at run
time): unresolved cosmolike-side integration shows up as an apparent
CAMB sensitivity, so the cheap knobs must be settled before the
expensive one is blamed. `kmax_boltzmann` and CAMB `kmax` are one
physical cutoff seen from the two sides; move them together.
