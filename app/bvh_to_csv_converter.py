# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""BVH -> robot CSV converter entry point.

The v0.1-lineage pipeline now lives in ``bvh_to_csv_converter_legacy.py``
(``soma_retargeter.legacy``); this file keeps the documented command line
``python app/bvh_to_csv_converter.py --config <json> --viewer null`` working.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bvh_to_csv_converter_legacy import main  # noqa: E402

if __name__ == "__main__":
    main()
