# Unit tests for the des_y3 likelihoods

These tests catch two kinds of silent breakage: a $\chi^2$ that drifted
because code or data changed by accident, and a race condition (a bug
where evaluating several points in a row corrupts a later result
through leftover internal state or colliding OpenMP threads).

The project ships two generations of DES data, and the tests cover
both: tests 1-14 evaluate the DES-Y3 data (`des_y3_real.dataset`),
tests 15-26 evaluate the DES-Y1 data (`des_y1_real.dataset`) through
the same `des_y3.*` likelihood classes.

Every model build runs in its own worker subprocess: the Y1 and Y3
data sets have different masked dimensions and n(z) table lengths,
and the cosmolike C layer aborts the whole process when a second
configuration with different dimensions initializes after the first.
The isolation is internal; the commands below stay the same.

# Table of contents

1. [Running the tests](#run_tests)
2. [The 24 tests](#the_tests)
    1. [Running Accuracy checks](#accuracy_checks)
    2. [Synthetic data vectors](#synthetic_vectors)
3. [Appendices about the frozen state](#appendix)
    1. [FAQ: How do the tests keep their own copy of configurations and data?](#frozen_copy)
    2. [FAQ: How can maintainers refresh the frozen state?](#refreeze)

## Running the tests <a name="run_tests"></a>

We assume users are in the Conda cocoa environment from a previous
`conda activate cocoa` command, that the shell is bash, and that the
current folder is the cocoa main folder `cocoa/Cocoa`.

**Step :one:**: activate the private Python environment by sourcing
the script `start_cocoa.sh`

    source start_cocoa.sh

**Step :two:**: run the tests of this project

    python -m pytest ./projects/des_y3/tests

Without pytest:

    python -m unittest discover -s ./projects/des_y3/tests -v

The tests change no project files. Each test prints a progress line
per model build and per evaluation, then a report with the
computed $\chi^2$, the stored reference, the difference, and the pass
limit.

A full run performs about 150 likelihood evaluations and takes
a few minutes. The test files force `OMP_NUM_THREADS=4` internally.

## The 24 tests <a name="the_tests"></a>

The standard configurations get four tests each: a $\chi^2$ drift check
and a race check, both in the NLA and in the TATT intrinsic-alignment
model. The TATT variants set

    IA_model: 1
    DES_A2_1: 0.05
    DES_BTA_1: 0.05
    DES_A2_2: -1.51541

The two checks and their pass limits:

| check | pass limit                                        | a failure means                    |
|-------|---------------------------------------------------|------------------------------------|
| $\chi^2$  | within 0.2 of `frozen/reference_chi2.json`        | code or data changed the numbers   |
| race  | fresh vs 10th of 10 cosmologies in a row, to $10^{-4}$ | leftover state or an OpenMP race   |

The test files and the configurations they cover:

| tests | file | data | configuration |
|-------|------|------|---------------|
| 1-4   | `test_example1.py` | DES-Y3 | cosmic shear (example1) |
| 5-8   | `test_example2.py` | DES-Y3 | 3x2pt (example2) |
| 11-14 | `test_example2_2x2pt.py` | DES-Y3 | 2x2pt (`des_y3.combo_2x2pt`) |
| 15-18 | `test_example3.py` | DES-Y1 | cosmic shear (example3) |
| 19-22 | `test_example4.py` | DES-Y1 | 3x2pt (example4) |
| 23-26 | `test_example4_2x2pt.py` | DES-Y1 | 2x2pt (`des_y3.combo_2x2pt`) |

### Running Accuracy checks (`test_accuracy.py`, A1-A12) <a name="accuracy_checks"></a>

The three probes with
both IA models on both data sets (A1-A6 des_y3, A7-A12 des_y1),
re-evaluated with every setting pushed far beyond the defaults at
once. A one-knob-at-a-time scan on the des_y3 example2 NLA
configuration runs first, so a large all-knobs delta can be
attributed to the knob causing it. The all-knobs settings:

| setting | raised to | what it controls |
|---------|-----------|------------------|
| `accuracyboost` (cosmolike) | 2 | sizes of cosmolike's internal lookup tables, including the dyadic z grid of the power-spectrum tables |
| `integration_accuracy` (cosmolike) | 10 | extra refinement passes of cosmolike's numerical integrals |
| `lmax` (cosmolike) | 200000 | highest multipole in cosmolike's angular power-spectrum tables |
| `kmax_boltzmann` (cosmolike) | 40 | the k cutoff of the power spectrum the likelihood requests from CAMB |
| `AccuracyBoost` (CAMB) | 2 | CAMB's overall accuracy multiplier: denser sampling in every internal CAMB grid, the most expensive knob |
| `k_per_logint` (CAMB) | 50 | k samples CAMB computes per logarithmic interval of the transfer functions |
| `kmax` (CAMB) | 50 | highest k of CAMB's matter power spectrum; one physical cutoff with `kmax_boltzmann`, seen from the CAMB side |

Each check reports $\Delta\chi^2 = \chi^2(\text{high accuracy}) -
\chi^2(\text{default})$: the numerical error of the default
settings. No pass/fail; high-accuracy evaluations take minutes.

**Step :one:**: with the environment of
[Running the tests](#run_tests), run the accuracy checks on their own

    python -m pytest ./projects/des_y3/tests/test_accuracy.py

To run every other test while skipping these:

    python -m pytest ./projects/des_y3/tests --ignore ./projects/des_y3/tests/test_accuracy.py

### Synthetic data vectors <a name="synthetic_vectors"></a>

This project's shipped data vectors are REAL data (the DES-Y3 and
DES-Y1 measurements), and the example cosmology is not a best fit of
either, so the $\chi^2$ there sits far from the minimum, where it
responds linearly to tiny numerical changes. Every variant therefore
evaluates against a data vector generated at the fiducial point
during the freeze, one pair per data set:

| data | NLA vector | TATT vector | generated from |
|------|-----------|-------------|----------------|
| DES-Y3 | `frozen/data/synthetic_des_y3.dataset` | `frozen/data/tatt_des_y3.dataset` | the example2 (3x2pt) model |
| DES-Y1 | `frozen/data/synthetic_des_y1.dataset` | `frozen/data/tatt_des_y1.dataset` | the example4 model |

Within a data set the full-length 3x2pt vector serves every probe
(the masks select their sections); at its own minimum the $\chi^2$
response is quadratic and the drift and accuracy numbers stay
meaningful.

# Appendices about the frozen state <a name="appendix"></a>

## :interrobang: FAQ: How do the tests keep their own copy of configurations and data? <a name="frozen_copy"></a>

The tests read nothing from the live project: not `../data`, not the
`EXAMPLE_EVALUATE` yaml files, and not the likelihood default yaml
files. Instead, `frozen/` holds:

| `frozen/` entry | holds |
|---|---|
| `frozen_config_example*.py` | the complete cobaya configuration as a yaml string, plus the exact evaluation point |
| `data/` | the tests' own copy of the data vectors, covariances, n(z), and masks of both data sets |
| `EXAMPLE_EVALUATE{1,2,3,4}.yaml` | snapshots kept only so a human can diff how the live examples drifted since the freeze |

In the configuration modules every option and every parameter is
written out, including the ones that normally come from
`params_source.yaml` and the other default files, so editing those
files cannot change what the tests evaluate.


`manifest_sha256.json` stores a SHA-256 hash (a fingerprint that
changes when any byte changes) of every frozen file. Each test
verifies the manifest first and refuses to run when a frozen file was
edited, naming the file. The result: users may change the live data
and examples freely, and nobody can quietly edit the frozen state
either.

## :interrobang: FAQ: How can maintainers refresh the frozen state? <a name="refreeze"></a>

A deliberate change to the data vectors, n(z), covariance, examples,
or likelihood defaults requires a re-freeze.

**Step :one:**: set up the environment as in
[Running the tests](#run_tests).

**Step :two:**: rebuild the frozen state

    python ./projects/des_y3/tests/generate_frozen_reference.py --overwrite

It rebuilds `frozen/` from the current project, prints the twelve new
reference $\chi^2$ values, and rewrites the manifest. Review the printed
$\chi^2$ values against the old references before committing: they define
what every later test run compares against.
