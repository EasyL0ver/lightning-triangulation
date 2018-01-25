import templates
from Data import dataprovider as dp
from Data import datamodels
from Modules import filtering as pre
from Modules import plot
from Modules import threshold as th

debug_plot_blocks_enabled = False
show_all_obs = False
show_all_events = False
show_single_events = False
show_all_files = False
show_all_files_fft = False
deconvolution_test_on = False
dynamic_sys_test_on = True

view_deconvolution_on = False
deconvolution_mask_path = r"D:\inzynierka\ImpulseDataAnalyzer\gf_ELA10v6_NEW.data",

#setupdatastorage and converter
dataprov = dp.DataProvider(drop_db=False);
dataprov.populate()

#show all observations example
observations = dataprov.orm_provider.get_session().query(datamodels.Observation).order_by(
    datamodels.Observation.certain.desc()).all()
if show_all_obs:
    flt = templates.pre_processing_template()
    deconvolution_block = pre.DeconvolutionBlock(deconvolution_mask_path,
                                                 view_deconvolution_on)
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
    deconvolution_block = pre.DeconvolutionBlock(deconvolution_mask_path,
                                                 view_deconvolution_on)
    boundary_effect_block = th.BoundaryZeroBlock(200)
    fiplot = plot.FilePlotBlock()

    plot_instance.children().append(deconvolution_block)
    deconvolution_block.children().append(boundary_effect_block)
    boundary_effect_block.children().append(fiplot)
    for file in files:
        plot_instance.on_enter(file.load_data())

#files fft example
if show_all_files_fft:
    files = dataprov.orm_provider.get_session().query(datamodels.File).all()
    plot_instance = templates.pre_processing_template()
    fiplot = plot.FilePlotBlock(mode='fft')

    plot_instance.children().append(fiplot)
    for file in files:
        plot_instance.on_enter(file.load_data())

if deconvolution_test_on:
    files = dataprov.orm_provider.get_session().query(datamodels.File).all()
    plot_instance = templates.pre_processing_template()
    test_deconv = pre.ResamplingFFTDeconvolution(deconvolution_mask_path, 266335)
    fiplot = plot.BaseAsyncPlotBlock(1, True, 'sn', 'dec')

    plot_instance.children().append(test_deconv)
    test_deconv.children().append(fiplot)
    for file in files:
        plot_instance.on_enter(file.load_data())


if dynamic_sys_test_on:
    #change dynamic system output for this to work
    flt = templates.pre_processing_template()
    deconvolution_block = pre.DeconvolutionBlock(deconvolution_mask_path,
                                                 view_deconvolution_on)
    power_block = th.PowerBlock()
    dyn_sys = th.BasicDynamicSystem("pwr", 50, 5, 7, span=4)
    oplot = plot.BaseAsyncPlotBlock(1, True, "pwr", "dyn_pwr")

    flt.children().append(deconvolution_block)
    deconvolution_block.children().append(power_block)
    power_block.children().append(dyn_sys)
    dyn_sys.children().append(oplot)

    for obs in observations:
        flt.on_enter(obs.get_data())






