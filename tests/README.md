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

## Running the tests

From the `Cocoa/` folder, with the cocoa conda environment active and
`start_cocoa.sh` sourced:

    python -m pytest ./projects/des_y3/tests

Without pytest:

    python -m unittest discover -s ./projects/des_y3/tests -v

The tests change no project files. Each test streams a progress line
per model build and per evaluation, then a report block with the
computed $\chi^2$, the stored reference, the difference, and the pass
limit. A full run performs about 150 likelihood evaluations and takes
a few minutes. The test modules force `OMP_NUM_THREADS=4` internally.
The tests never stop to ask for input. If the terminal pauses until
space or enter is pressed, something sent the output through `less`
(a program that stops after each full screen): run the commands
exactly as written above, with nothing added after them.

## The 24 tests

The standard configurations get four tests each: a $\chi^2$ drift check
and a race check, both in the NLA and in the TATT intrinsic-alignment
model. The TATT variants set

    IA_model: 1
    DES_A2_1: 0.05
    DES_BTA_1: 0.05
    DES_A2_2: -1.51541

| check | pass limit                                        | a failure means                    |
|-------|---------------------------------------------------|------------------------------------|
| $\chi^2$  | within 0.2 of `frozen/reference_chi2.json`        | code or data changed the numbers   |
| race  | fresh vs 10th of 10 cosmologies in a row, to $10^{-4}$ | leftover state or an OpenMP race   |

| tests | file | data | configuration |
|-------|------|------|---------------|
| 1-4   | `test_example1.py` | DES-Y3 | cosmic shear (example1) |
| 5-8   | `test_example2.py` | DES-Y3 | 3x2pt (example2) |
| 11-14 | `test_example2_2x2pt.py` | DES-Y3 | 2x2pt (`des_y3.combo_2x2pt`) |
| 15-18 | `test_example3.py` | DES-Y1 | cosmic shear (example3) |
| 19-22 | `test_example4.py` | DES-Y1 | 3x2pt (example4) |
| 23-26 | `test_example4_2x2pt.py` | DES-Y1 | 2x2pt (`des_y3.combo_2x2pt`) |

Accuracy checks (`test_accuracy.py`, A1-A12): the three probes with
both IA models on both data sets (A1-A6 des_y3, A7-A12 des_y1),
re-evaluated with every setting pushed far beyond the defaults at
once. A one-knob-at-a-time scan on the des_y3 example2 NLA
configuration runs first, so a large all-knobs delta can be
attributed to the knob causing it. The all-knobs settings:

    # cosmolike likelihood settings
    accuracyboost: 2
    integration_accuracy: 10
    lmax: 200000
    kmax_boltzmann: 40
    # CAMB extra_args (kmax moves with kmax_boltzmann: one physical cutoff)
    AccuracyBoost: 2
    k_per_logint: 50
    kmax: 50

Each check reports $\Delta\chi^2 = \chi^2(\text{high accuracy}) -
\chi^2(\text{default})$: the numerical error of the default
settings. No pass/fail. High-accuracy evaluations take minutes; run
the file on its own, or skip it with

    python -m pytest ./projects/des_y3/tests --ignore ./projects/des_y3/tests/test_accuracy.py

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

## Why the tests keep their own copy of everything

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

## Refreshing the frozen state (maintainers only)

A deliberate change to the data vectors, n(z), covariance, examples,
or likelihood defaults requires a re-freeze:

    python ./projects/des_y3/tests/generate_frozen_reference.py --overwrite

Run it from the `Cocoa/` folder with the environment set up as above.
It rebuilds `frozen/` from the current project, prints the twelve new
reference $\chi^2$ values, and rewrites the manifest. Review the printed
$\chi^2$ values against the old references before committing: they define
what every later test run compares against.
