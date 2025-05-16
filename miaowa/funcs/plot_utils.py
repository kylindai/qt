import re
import talib
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import mplfinance as mpf

from typing import List, Dict, Tuple, Set


class PlotUtil:

    @staticmethod
    def show_plot(title: str,
                  bar_df: pd.DataFrame,
                  plot_type: str = "hollow_and_filled"):
        """
        """
        bar_df.columns = ['open', 'high', 'low', 'close', 'volume', 
                          'ask_price', 'ask_volume', 'bid_price', 'bid_volume']
        
        # color
        plot_color = mpf.make_marketcolors(up='r',
                                           down='g',
                                           edge='inherit',
                                           wick='inherit',
                                           volume='inherit')
        # style
        plot_style = mpf.make_mpf_style(base_mpf_style='yahoo',
                                        edgecolor='black',
                                        # marketcolors=plot_color,
                                        figcolor='#FFF',
                                        gridstyle=':',
                                        rc={'font.family': 'monospace', 'axes.unicode_minus': False},
                                        y_on_right=False)
        # plot_style['marketcolors']['volume'] = {'up': 'lightgreen', 'down':'lightcoral'}

        apds = PlotUtil.make_bar_plot(bar_df)

        volume_panel, panel_ratios = PlotUtil.make_pannel_param(apds)

        plot_kws = dict(title=title,
                        figsize=(16, 8),
                        figscale=3,
                        figratio=(1, 1),
                        tight_layout=True,
                        fontscale=0.8,
                        # mav=(5,10,20),
                        volume=True,
                        ylabel='',
                        ylabel_lower='',
                        volume_panel=volume_panel,
                        volume_alpha=0.8,
                        update_width_config=dict(line_width=1,
                                                 candle_width=0.6,
                                                 volume_linewidth=0),
                        # volume_yscale='linear',
                        style=plot_style,
                        type=plot_type,
                        xrotation=0,
                        panel_ratios=panel_ratios,
                        show_nontrading=False,
                        datetime_format='%m-%d %H:%M:%S')
        
        if len(apds) > 0:
            mpf.plot(bar_df, **plot_kws, addplot=apds)
        else:
            mpf.plot(bar_df, **plot_kws)
        
    @staticmethod
    def make_pannel_param(apds: List):
        """
        - volume_panel
        - panel_ratios
        """
        # main panel for price
        panel_ratios = [1]
        has_panel = [True, False, False, False]
        # add other panel
        for _, apd in enumerate(apds):
            panel = apd['panel']
            # print(panel, apd['mw.name'])
            if panel == 0 and not has_panel[0]:
                panel_ratios.append(1)
                has_panel[0] = True
            if panel == 1 and not has_panel[panel]:
                panel_ratios.append(0.3)
                has_panel[panel] = True
            if panel == 2 and not has_panel[panel]:
                panel_ratios.append(0.3)
                has_panel[panel] = True
            if panel == 3 and not has_panel[panel]:
                panel_ratios.append(0.3)
                has_panel[panel] = True
        # last panel for volume
        if len(panel_ratios) == 1:
            panel_ratios.append(0.3)
        volume_panel = len(panel_ratios) - 1
        return (volume_panel, panel_ratios)
            

    @staticmethod
    def make_bar_plot(bar_df: pd.DataFrame, load_ask_bid: bool = True):
        """
        :param bar_df
        """
        apds = []
        if load_ask_bid:
            apds.extend(PlotUtil.make_bid_plot(bar_df['bid_volume']))
            apds.extend(PlotUtil.make_ask_plot(bar_df['ask_volume']))
        return apds

    @staticmethod
    def make_ask_plot(series: pd.Series, panel: int = 0):
        apds = []
        linestyle = 'dotted'  # dotted
        apd = mpf.make_addplot(series / 1000.0,
                               panel=panel, type='bar', color='sandybrown', secondary_y=True,
                               width=1, alpha=0.1, label="")
        apd['mw.name'] = 'A.V'
        apds.append(apd)
        return apds

    @staticmethod
    def make_bid_plot(series: pd.Series, panel: int = 0):
        apds = []
        linestyle = 'dotted'  # dotted
        apd = mpf.make_addplot(series / 1000.0,
                               panel=panel, type='bar', color='dodgerblue', secondary_y=True,
                               width=1, alpha=0.1, label="")
        apd['mw.name'] = 'B.V'
        apds.append(apd)
        return apds
