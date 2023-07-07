# Automated Skew Analysis powered by pyAEDT - v0.1

## Pre-requisites

`PyAEDT` - more information about it [here](https://github.com/ansys/pyaedt)

`Ansys Electronics Desktop` - more information about it [here](https://www.ansys.com/products/electronics)


## How to use it?

1. On a text editor/IDE of your choice, open the file [SparamSkewCheck.py](https://github.com/felipeescastro/skewAnalysiswithpyAEDT/blob/main/SparamSkewCheck.py) and modify the inputs as seen below:
   ``` python
      inputSparam = r"D:\Scripts\aapyAEDT\SparamDelayCheck\hbm_dqh7_13_notsv_0ord_solvIns.s12p"
      drvName = "N7"
      rcvName = "HBM"
      portNamingConventionSeparator = '.' # i.e: current portNamingConvention="$REFDES.$PINNAME.$NETNAME"
      diffPairSuffix_pos = "_t"
      diffPairSuffix_neg = "_c"
      drv_datarate="3.2GHz"
   
      desktop_version = "2023.1"
      non_graphical = False
      new_thread = True
   ```
2. Save it and run it in your `PyAEDT` virtual environment or, starting on `Ansys Electronics Desktop` 2023R2, you can run it via the tab Automation > PyAEDT > Run PyAEDT Script

## License

`PyAEDT` is licensed under the `MIT` license.

This module makes no commercial claim over Ansys whatsoever. `PyAEDT` extends the functionality of `AEDT` by adding an additional Python interface to `AEDT` without changing the core behavior or license of the original software. The use of the interactive control of `PyAEDT` requires a legally licensed local copy of `AEDT`. For more information about `AEDT`, visit the [AEDT page](https://www.ansys.com/products/electronics) on the `Ansys` website.
