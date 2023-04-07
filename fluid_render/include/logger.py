class Logger:
    FRAME_START = 0
    SIMULATE_START = 1
    SIMULATE_END = 2
    RENDER_START = 3
    RENDER_END = 4
    ADVECT_START = 5
    ADVECT_END = 6
    GRID_START = 7
    GRID_END = 8
    DENSITY_START = 9
    DENSITY_END = 10
    VELOCITY_UPDATE_START = 11
    VELOCITY_UPDATE_END = 12
    VELOCITY_CORRECT_START = 13
    VELOCITY_CORRECT_END = 14
    DEPTH_START = 15
    DEPTH_END = 16
    THICK_START = 17
    THICK_END = 18
    SMOOTH_START = 19
    SMOOTH_END = 20
    NORMAL_START = 21
    NORMAL_END = 22
    SHADING_START = 23
    SHADING_END = 24

    def __init__(self):
        self.nframe = None

        self.simu_bg, self.simu_sum, self.simu_min, self.simu_max = [0] * 4
        self.render_bg, self.render_sum, self.render_min, self.render_max = [0] * 4
        self.advect_bg, self.advect_sum, self.advect_min, self.advect_max = [0] * 4
        self.grid_bg, self.grid_sum, self.grid_min, self.grid_max = [0] * 4
        self.density_bg, self.density_sum, self.density_min, self.density_max = [0] * 4
        self.vel_upd_bg, self.vel_upd_sum, self.vel_upd_min, self.vel_upd_max = [0] * 4
        self.vel_corr_bg, self.vel_corr_sum, self.vel_corr_min, self.vel_corr_max = [0] * 4
        self.depth_bg, self.depth_sum, self.depth_min, self.depth_max = [0] * 4
        self.thick_bg, self.thick_sum, self.thick_min, self.thick_max = [0] * 4
        self.smooth_bg, self.smooth_sum, self.smooth_min, self.smooth_max = [0] * 4
        self.normal_bg, self.normal_sum, self.normal_min, self.normal_max = [0] * 4
        self.shading_bg, self.shading_sum, self.shading_min, self.shading_max = [0] * 4

        # enable/disable logging of time taken for each section of the code.
        # if disabled (default), only the number of frames is logged.
        # if enabled (via toggleLogTime), time taken for each section is also logged.
        # note that enabling this will slow down the simulation.
        # logging can be enabled/disabled at any time during the simulation.
        # logging can be enabled/disabled at any time during the simulation.
        # logging can be enabled/disabled at any time during the simulation.
        # logging can be enabled/disabled at any time during the simulation.
        # logging can be enabled/disabled at any time during the simulation.
        # logging can be enabled/disabled at any time during the simulation.
        # logging can be enabled/disabled at any time during the simulation.
        # logging can be enabled/disabled at any time during the simulation.
        # logging can be enabled/disabled at any time during the simulation.
        # logging can be enabled/disabled at any time during the simulation.