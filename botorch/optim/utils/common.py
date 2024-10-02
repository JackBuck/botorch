#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

r"""General-purpose optimization utilities."""

from __future__ import annotations

from collections.abc import Callable

from logging import debug as logging_debug
from warnings import warn_explicit, WarningMessage

import numpy as np
from linear_operator.utils.errors import NanError, NotPSDError


def _handle_numerical_errors(
    error: RuntimeError, x: np.ndarray, dtype: np.dtype | None = None
) -> tuple[np.ndarray, np.ndarray]:
    if isinstance(error, NotPSDError):
        raise error
    error_message = error.args[0] if len(error.args) > 0 else ""
    if (
        isinstance(error, NanError)
        or "singular" in error_message  # old pytorch message
        or "input is not positive-definite" in error_message  # since pytorch #63864
    ):
        _dtype = x.dtype if dtype is None else dtype
        return np.full((), "nan", dtype=_dtype), np.full_like(x, "nan", dtype=_dtype)
    raise error  # pragma: nocover


def _warning_handler_template(
    w: WarningMessage,
    debug: Callable[[WarningMessage], bool] | None = None,
    rethrow: Callable[[WarningMessage], bool] | None = None,
) -> bool:
    r"""Helper for making basic warning handlers. Typically used with functools.partial.

    Args:
        w: The WarningMessage to be resolved and filtered out or returned unresolved.
        debug: Optional callable used to specify that a warning should be
            resolved as a logging statement at the DEBUG level.
        rethrow: Optional callable used to specify that a warning should be
            resolved by rethrowing the warning.

    Returns:
        Boolean indicating whether or not the warning message was resolved.
    """
    if debug and debug(w):
        logging_debug(str(w.message))
        return True

    if rethrow and rethrow(w):
        warn_explicit(str(w.message), w.category, w.filename, w.lineno)
        return True

    return False
