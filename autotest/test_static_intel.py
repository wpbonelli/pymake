"""Tests for linking the intel fortran runtime statically vs dynamically.

An ifort/ifx-built target on osx or linux is meant to statically link the
intel runtime by default, whether it is an executable or a shared object, so
that it does not depend on the intel runtime being installed on the machine
that runs it. A caller can still ask for the intel default (dynamic linking)
explicitly with -shared-intel.

Cases:
  - test_static_intel_default_for_executable : an ifort executable gets
    -static-intel by default on osx and linux.
  - test_static_intel_default_for_sharedobject : an ifort shared object
    gets -static-intel by default too (previously the only case that did).
  - test_shared_intel_opts_out : -shared-intel in the requested syslibs
    is honored instead of the static-intel default.
  - test_gfortran_unaffected : a gfortran target is not given -static-intel,
    since only ifort/ifx provide it.
  - test_static_intel_kept_for_executable : Pymake no longer strips
    -static-intel from a non-shared target's syslibs.
  - test_syslibs_not_limited_to_lc_lm : the make-program --syslibs option
    accepts a flag other than -lc or -lm.
"""

import pytest

from pymake import Pymake
from pymake.cmds.build import build_parser
from pymake.utils._compiler_switches import _get_linker_flags


@pytest.mark.base
@pytest.mark.parametrize("osname", ["linux", "darwin"])
def test_static_intel_default_for_executable(osname) -> None:
    """An ifort executable gets -static-intel by default on osx and linux."""
    _, flags = _get_linker_flags(
        "mp7", "ifort", None, [], ["main.f90"], sharedobject=False, osname=osname
    )

    assert "-static-intel" in flags, (
        f"an ifort executable is not statically linked by default: {flags}"
    )


@pytest.mark.base
def test_static_intel_default_for_sharedobject() -> None:
    """An ifort shared object gets -static-intel by default too."""
    _, flags = _get_linker_flags(
        "libmf6", "ifort", None, [], ["main.f90"], sharedobject=True, osname="linux"
    )

    assert "-static-intel" in flags, (
        f"an ifort shared object is not statically linked by default: {flags}"
    )


@pytest.mark.base
def test_shared_intel_opts_out() -> None:
    """-shared-intel in the requested syslibs is honored over the default."""
    _, flags = _get_linker_flags(
        "mp7",
        "ifort",
        None,
        ["-shared-intel"],
        ["main.f90"],
        sharedobject=False,
        osname="linux",
    )

    assert "-static-intel" not in flags, (
        f"-shared-intel did not opt out of the static-intel default: {flags}"
    )
    assert "-shared-intel" in flags, f"-shared-intel was dropped: {flags}"


@pytest.mark.base
def test_gfortran_unaffected() -> None:
    """A gfortran target is not given -static-intel."""
    _, flags = _get_linker_flags(
        "mp7", "gfortran", None, [], ["main.f90"], sharedobject=False, osname="linux"
    )

    assert "-static-intel" not in flags, (
        f"-static-intel was added for a non-intel compiler: {flags}"
    )


@pytest.mark.base
def test_static_intel_kept_for_executable() -> None:
    """Pymake no longer strips -static-intel from a non-shared target."""
    pm = Pymake()
    pm.target = "mp7"
    pm.syslibs = "-static-intel"

    pm._set_sharedobject()

    assert pm.sharedobject is False
    assert pm.syslibs == "-static-intel", (
        f"-static-intel was stripped from an executable's syslibs: {pm.syslibs!r}"
    )


@pytest.mark.base
def test_syslibs_not_limited_to_lc_lm() -> None:
    """The make-program --syslibs option accepts a flag other than -lc/-lm."""
    args = build_parser().parse_args(["mp7", "--syslibs=-static-intel"])

    assert args.syslibs == "-static-intel", (
        f"--syslibs rejected a flag outside its old choices: {args.syslibs!r}"
    )
