import templates
from Data import dataprovider as dp
from Data import datamodels
from Modules import filtering as pre
from Modules import plot

debug_plot_blocks_enabled = False
show_all_obs = False
show_all_events = False
show_single_events = False
show_all_files = False
show_all_files_fft = True

view_deconvolution_on = False

#setupdatastorage and converter
dataprov = dp.DataProvider(drop_db=False);
dataprov.populate()

#show all observations example
observations = dataprov.orm_provider.get_session().query(datamodels.Observation).order_by(
    datamodels.Observation.certain.desc()).all()
if show_all_obs:
    flt = templates.pre_processing_template()
    deconvolution_block = pre.DeconvolutionBlock(r"D:\inzynierka\ImpulseDataAnalyzer\gf_ELA10v6_NEW.data")
    oplot = plot.ObservationPlotBlock()

    flt.children().append(deconvolution_block)
    deconvolution_block.children().append(oplot)
    for obs in observations:
        flt.on_enter(obs.get_data())

#events plot example
if show_all_events:
    pass

if show_single_events:
    events = dataprov.orm_provider.get_session().query(datamodels.Event).all()
    evplot = plot.EventPlotBlock(dsp_template_instance=templates.pre_processing_template())
    for event in events:
        evplot.on_enter(event.get_data())

#files plot example
if show_all_files:
    files = dataprov.orm_provider.get_session().query(datamodels.File).all()
    plot_instance = templates.pre_processing_template()
    deconvolution_block = pre.DeconvolutionBlock(r"D:\inzynierka\ImpulseDataAnalyzer\gf_ELA10v6_NEW.data")
    fiplot = plot.FilePlotBlock()

    plot_instance.children().append(deconvolution_block)
    deconvolution_block.children().append(fiplot)
    for file in files:
        plot_instance.on_enter(file.load_data())

#files fft example
if show_all_files_fft:
    files = dataprov.orm_provider.get_session().query(datamodels.File).all()
    plot_instance = templates.pre_processing_template()
    fiplot = plot.FftPlotBlock(1, True, 'sn')

    plot_instance.children().append(fiplot)
    for file in files:
        plot_instance.on_enter(file.load_data())









