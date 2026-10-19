{
  "patcher": {
    "fileversion": 1,
    "appversion": {
      "major": 8,
      "minor": 6,
      "revision": 5,
      "architecture": "x64",
      "modernui": 1
    },
    "classnamespace": "box",
    "rect": [
      100,
      100,
      900,
      700
    ],
    "bglocked": 0,
    "openinpresentation": 1,
    "default_fontsize": 12.0,
    "default_fontface": 0,
    "default_fontname": "Arial",
    "gridonopen": 1,
    "gridsize": [
      15.0,
      15.0
    ],
    "gridsnaponopen": 1,
    "objectsnaponopen": 1,
    "statusbarvisible": 2,
    "toolbarvisible": 1,
    "lefttoolbarpinned": 0,
    "toptoolbarpinned": 0,
    "righttoolbarpinned": 0,
    "bottomtoolbarpinned": 0,
    "toolbars_unpinned_last_save": 0,
    "tallnewobj": 0,
    "boxanimatetime": 200,
    "enablehscroll": 1,
    "enablevscroll": 1,
    "devicewidth": 350,
    "description": "Audio-to-OSC signal router. Envelope-follows audio and sends normalized 0-1 floats over OSC.",
    "digest": "Audio-to-OSC signal routing for external control systems.",
    "tags": "signal osc envelope",
    "style": "",
    "subpatcher_template": "",
    "boxes": [
      {
        "box": {
          "id": "obj-1",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "signal",
            "signal"
          ],
          "patching_rect": [
            50.0,
            80.0,
            55.0,
            22.0
          ],
          "text": "plugin~"
        }
      },
      {
        "box": {
          "id": "obj-2",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ],
          "patching_rect": [
            50.0,
            120.0,
            79.0,
            22.0
          ],
          "text": "abs~"
        }
      },
      {
        "box": {
          "id": "obj-attack-ms2samps",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ],
          "patching_rect": [
            250.0,
            160.0,
            64.0,
            22.0
          ],
          "text": "mstosamps~"
        }
      },
      {
        "box": {
          "id": "obj-release-ms2samps",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ],
          "patching_rect": [
            350.0,
            160.0,
            64.0,
            22.0
          ],
          "text": "mstosamps~"
        }
      },
      {
        "box": {
          "id": "obj-attack-sig",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ],
          "patching_rect": [
            250.0,
            130.0,
            33.0,
            22.0
          ],
          "text": "sig~"
        }
      },
      {
        "box": {
          "id": "obj-release-sig",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ],
          "patching_rect": [
            350.0,
            130.0,
            33.0,
            22.0
          ],
          "text": "sig~"
        }
      },
      {
        "box": {
          "id": "obj-3",
          "maxclass": "newobj",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ],
          "patching_rect": [
            50.0,
            200.0,
            320.0,
            22.0
          ],
          "text": "slide~ 220 2205"
        }
      },
      {
        "box": {
          "id": "obj-meter",
          "maxclass": "live.meter~",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "list"
          ],
          "patching_rect": [
            160.0,
            240.0,
            10.0,
            60.0
          ],
          "presentation": 1,
          "presentation_rect": [
            15.0,
            55.0,
            320.0,
            12.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-4",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "float",
            ""
          ],
          "patching_rect": [
            50.0,
            260.0,
            76.0,
            22.0
          ],
          "text": "snapshot~ 16"
        }
      },
      {
        "box": {
          "id": "obj-invert-expr",
          "maxclass": "newobj",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            50.0,
            370.0,
            115.0,
            22.0
          ],
          "text": "expr $f1 + $i2 * (1. - 2.*$f1)"
        }
      },
      {
        "box": {
          "id": "obj-clip",
          "maxclass": "newobj",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            50.0,
            400.0,
            73.0,
            22.0
          ],
          "text": "clip 0. 1."
        }
      },
      {
        "box": {
          "id": "obj-active-gate",
          "maxclass": "newobj",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            50.0,
            430.0,
            60.0,
            22.0
          ],
          "text": "gate 1 1"
        }
      },
      {
        "box": {
          "id": "obj-value-display",
          "maxclass": "flonum",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            200.0,
            430.0,
            50.0,
            22.0
          ],
          "presentation": 1,
          "presentation_rect": [
            280.0,
            55.0,
            55.0,
            22.0
          ],
          "numdecimalplaces": 3
        }
      },
      {
        "box": {
          "id": "obj-prepend-prefix",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            50.0,
            500.0,
            120.0,
            22.0
          ],
          "text": "prepend /Params/Param1"
        }
      },
      {
        "box": {
          "id": "obj-udpsend",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            50.0,
            540.0,
            155.0,
            22.0
          ],
          "text": "udpsend 127.0.0.1 3333"
        }
      },
      {
        "box": {
          "id": "obj-port-msg",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            500.0,
            500.0,
            97.0,
            22.0
          ],
          "text": "prepend port"
        }
      },
      {
        "box": {
          "id": "obj-param-name",
          "maxclass": "live.menu",
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "",
            "",
            "float"
          ],
          "parameter_enable": 1,
          "parameter_mappable": 1,
          "patching_rect": [
            500.0,
            160.0,
            100.0,
            15.0
          ],
          "presentation": 1,
          "presentation_rect": [
            15.0,
            10.0,
            200.0,
            20.0
          ],
          "saved_attribute_attributes": {
            "valueof": {
              "parameter_longname": "Param Name",
              "parameter_shortname": "Param",
              "parameter_type": 2,
              "parameter_enum": "Param1 Param2 Param3 Param4 Param5 Param6 Param7 Param8",
              "parameter_mmax": 7,
              "parameter_initial_enable": 1,
              "parameter_initial": [
                0
              ]
            }
          },
          "varname": "ParamName"
        }
      },
      {
        "box": {
          "id": "obj-active",
          "maxclass": "live.toggle",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "parameter_enable": 1,
          "parameter_mappable": 1,
          "patching_rect": [
            450.0,
            80.0,
            24.0,
            24.0
          ],
          "presentation": 1,
          "presentation_rect": [
            320.0,
            10.0,
            20.0,
            20.0
          ],
          "saved_attribute_attributes": {
            "valueof": {
              "parameter_longname": "Active",
              "parameter_shortname": "Active",
              "parameter_type": 2,
              "parameter_mmax": 1,
              "parameter_initial_enable": 1,
              "parameter_initial": [
                1
              ]
            }
          },
          "varname": "Active"
        }
      },
      {
        "box": {
          "id": "obj-attack",
          "maxclass": "live.dial",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "float"
          ],
          "parameter_enable": 1,
          "parameter_mappable": 1,
          "patching_rect": [
            250.0,
            80.0,
            44.0,
            48.0
          ],
          "presentation": 1,
          "presentation_rect": [
            15.0,
            80.0,
            44.0,
            48.0
          ],
          "saved_attribute_attributes": {
            "valueof": {
              "parameter_longname": "Attack",
              "parameter_shortname": "Atk",
              "parameter_type": 0,
              "parameter_unitstyle": 2,
              "parameter_mmin": 0.1,
              "parameter_mmax": 500.0,
              "parameter_initial_enable": 1,
              "parameter_initial": [
                5.0
              ],
              "parameter_exponent": 3.0
            }
          },
          "varname": "Attack"
        }
      },
      {
        "box": {
          "id": "obj-release",
          "maxclass": "live.dial",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "float"
          ],
          "parameter_enable": 1,
          "parameter_mappable": 1,
          "patching_rect": [
            350.0,
            80.0,
            44.0,
            48.0
          ],
          "presentation": 1,
          "presentation_rect": [
            80.0,
            80.0,
            44.0,
            48.0
          ],
          "saved_attribute_attributes": {
            "valueof": {
              "parameter_longname": "Release",
              "parameter_shortname": "Rel",
              "parameter_type": 0,
              "parameter_unitstyle": 2,
              "parameter_mmin": 0.1,
              "parameter_mmax": 2000.0,
              "parameter_initial_enable": 1,
              "parameter_initial": [
                50.0
              ],
              "parameter_exponent": 3.0
            }
          },
          "varname": "Release"
        }
      },
      {
        "box": {
          "id": "obj-gate-dial",
          "maxclass": "live.dial",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "float"
          ],
          "parameter_enable": 1,
          "parameter_mappable": 1,
          "patching_rect": [
            200.0,
            300.0,
            44.0,
            48.0
          ],
          "presentation": 1,
          "presentation_rect": [
            145.0,
            80.0,
            44.0,
            48.0
          ],
          "saved_attribute_attributes": {
            "valueof": {
              "parameter_longname": "Gate",
              "parameter_shortname": "Gate",
              "parameter_type": 0,
              "parameter_unitstyle": 1,
              "parameter_mmin": 0.0,
              "parameter_mmax": 1.0,
              "parameter_initial_enable": 1,
              "parameter_initial": [
                0.0
              ]
            }
          },
          "varname": "Gate"
        }
      },
      {
        "box": {
          "id": "obj-invert",
          "maxclass": "live.toggle",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "parameter_enable": 1,
          "parameter_mappable": 1,
          "patching_rect": [
            200.0,
            370.0,
            24.0,
            24.0
          ],
          "presentation": 1,
          "presentation_rect": [
            210.0,
            95.0,
            24.0,
            24.0
          ],
          "saved_attribute_attributes": {
            "valueof": {
              "parameter_longname": "Invert",
              "parameter_shortname": "Inv",
              "parameter_type": 2,
              "parameter_mmax": 1,
              "parameter_initial_enable": 1,
              "parameter_initial": [
                0
              ]
            }
          },
          "varname": "Invert"
        }
      },
      {
        "box": {
          "id": "obj-dest-port",
          "maxclass": "live.numbox",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "float"
          ],
          "parameter_enable": 1,
          "parameter_mappable": 1,
          "patching_rect": [
            500.0,
            460.0,
            56.0,
            15.0
          ],
          "presentation": 1,
          "presentation_rect": [
            285.0,
            95.0,
            50.0,
            15.0
          ],
          "saved_attribute_attributes": {
            "valueof": {
              "parameter_longname": "Dest Port",
              "parameter_shortname": "Port",
              "parameter_type": 0,
              "parameter_mmin": 1.0,
              "parameter_mmax": 65535.0,
              "parameter_initial_enable": 1,
              "parameter_initial": [
                3333.0
              ],
              "parameter_steps": 65535
            }
          },
          "varname": "DestPort"
        }
      },
      {
        "box": {
          "id": "obj-invert-label",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            230.0,
            376.0,
            45.0,
            20.0
          ],
          "presentation": 1,
          "presentation_rect": [
            210.0,
            80.0,
            30.0,
            20.0
          ],
          "text": "Inv",
          "fontsize": 9.0
        }
      },
      {
        "box": {
          "id": "obj-port-label",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            560.0,
            462.0,
            40.0,
            20.0
          ],
          "presentation": 1,
          "presentation_rect": [
            255.0,
            95.0,
            30.0,
            15.0
          ],
          "text": "Port",
          "fontsize": 9.0
        }
      },
      {
        "box": {
          "id": "obj-env-label",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            650.0,
            10.0,
            40.0,
            20.0
          ],
          "presentation": 1,
          "presentation_rect": [
            225.0,
            12.0,
            35.0,
            18.0
          ],
          "text": "ENV",
          "fontsize": 10.0,
          "textcolor": [
            0.3,
            0.7,
            0.3,
            1.0
          ],
          "fontface": 1
        }
      },
      {
        "box": {
          "id": "obj-plugout",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            50.0,
            600.0,
            60.0,
            22.0
          ],
          "text": "plugout~"
        }
      },
      {
        "box": {
          "id": "obj-gate-expr",
          "maxclass": "newobj",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            50.0,
            310.0,
            145.0,
            22.0
          ],
          "text": "expr $f1 * ($f1 >= $f2)"
        }
      },
      {
        "box": {
          "id": "obj-sprintf",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            500.0,
            220.0,
            150.0,
            22.0
          ],
          "text": "sprintf set /Params/%s"
        }
      }
    ],
    "lines": [
      {
        "patchline": {
          "source": [
            "obj-1",
            0
          ],
          "destination": [
            "obj-2",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-1",
            0
          ],
          "destination": [
            "obj-plugout",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-2",
            0
          ],
          "destination": [
            "obj-3",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-attack",
            0
          ],
          "destination": [
            "obj-attack-sig",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-attack-sig",
            0
          ],
          "destination": [
            "obj-attack-ms2samps",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-attack-ms2samps",
            0
          ],
          "destination": [
            "obj-3",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-release",
            0
          ],
          "destination": [
            "obj-release-sig",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-release-sig",
            0
          ],
          "destination": [
            "obj-release-ms2samps",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-release-ms2samps",
            0
          ],
          "destination": [
            "obj-3",
            2
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-3",
            0
          ],
          "destination": [
            "obj-meter",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-3",
            0
          ],
          "destination": [
            "obj-4",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-clip",
            0
          ],
          "destination": [
            "obj-value-display",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-invert",
            0
          ],
          "destination": [
            "obj-invert-expr",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-invert-expr",
            0
          ],
          "destination": [
            "obj-clip",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-clip",
            0
          ],
          "destination": [
            "obj-active-gate",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-active",
            0
          ],
          "destination": [
            "obj-active-gate",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-active-gate",
            0
          ],
          "destination": [
            "obj-prepend-prefix",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-prepend-prefix",
            0
          ],
          "destination": [
            "obj-udpsend",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-dest-port",
            0
          ],
          "destination": [
            "obj-port-msg",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-port-msg",
            0
          ],
          "destination": [
            "obj-udpsend",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-4",
            0
          ],
          "destination": [
            "obj-gate-expr",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-gate-dial",
            0
          ],
          "destination": [
            "obj-gate-expr",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-gate-expr",
            0
          ],
          "destination": [
            "obj-invert-expr",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-param-name",
            1
          ],
          "destination": [
            "obj-sprintf",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-sprintf",
            0
          ],
          "destination": [
            "obj-prepend-prefix",
            0
          ]
        }
      }
    ],
    "parameters": {
      "parameterbanks": {
        "0": {
          "index": 0,
          "name": "",
          "parameters": [
            "Param Name",
            "Active",
            "Attack",
            "Release",
            "Gate",
            "Invert",
            "Dest Port",
            "-"
          ]
        }
      },
      "inherited_shortname": 1
    },
    "dependency_cache": [],
    "autosave": 0
  }
}