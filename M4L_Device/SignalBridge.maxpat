{
	"patcher": {
		"fileversion": 1,
		"appversion": {
			"major": 9,
			"minor": 0,
			"revision": 8,
			"architecture": "x64",
			"modernui": 1
		},
		"classnamespace": "box",
		"rect": [
			134.0,
			100.0,
			1030.0,
			848.0
		],
		"openrect": [
			0.0,
			0.0,
			0.0,
			169.0
		],
		"openinpresentation": 1,
		"default_fontsize": 10.0,
		"default_fontname": "Arial Bold",
		"gridsize": [
			8.0,
			8.0
		],
		"boxanimatetime": 500,
		"boxes": [
			{
				"box": {
					"id": "obj-sb-osc-panel",
					"maxclass": "panel",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						700.0,
						400.0,
						100.0,
						50.0
					],
					"bgcolor": [
						0.156862745098039,
						0.156862745098039,
						0.156862745098039,
						1.0
					],
					"border": 0,
					"bordercolor": [
						0.0,
						0.0,
						0.0,
						0.0
					]
				}
			},
			{
				"box": {
					"color": [
						1.0,
						0.694117647058824,
						0.0,
						1.0
					],
					"id": "obj-55",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": [
						"",
						"",
						""
					],
					"patcher": {
						"fileversion": 1,
						"appversion": {
							"major": 9,
							"minor": 0,
							"revision": 8,
							"architecture": "x64",
							"modernui": 1
						},
						"classnamespace": "box",
						"rect": [
							608.0,
							245.0,
							682.0,
							350.0
						],
						"gridsize": [
							15.0,
							15.0
						],
						"boxes": [
							{
								"box": {
									"id": "obj-3",
									"maxclass": "message",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										554.0,
										157.0,
										65.0,
										22.0
									],
									"text": "26 4 130 4"
								}
							},
							{
								"box": {
									"id": "obj-2",
									"maxclass": "message",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										452.0,
										157.0,
										65.0,
										22.0
									],
									"text": "130 4 26 4"
								}
							},
							{
								"box": {
									"id": "obj-1",
									"maxclass": "message",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										452.0,
										196.0,
										123.0,
										22.0
									],
									"text": "setUiPos $1 $2 $3 $4"
								}
							},
							{
								"box": {
									"id": "obj-41",
									"maxclass": "message",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										89.0,
										157.0,
										29.5,
										22.0
									],
									"text": "2"
								}
							},
							{
								"box": {
									"id": "obj-32",
									"maxclass": "message",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										50.0,
										157.0,
										29.5,
										22.0
									],
									"text": "182"
								}
							},
							{
								"box": {
									"id": "obj-17",
									"maxclass": "message",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										50.0,
										196.0,
										287.0,
										22.0
									],
									"text": "script sendbox sc presentation_rect 23. $1 105. 168."
								}
							},
							{
								"box": {
									"id": "obj-43",
									"maxclass": "message",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										394.0,
										157.0,
										29.5,
										22.0
									],
									"text": "380"
								}
							},
							{
								"box": {
									"id": "obj-42",
									"maxclass": "message",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										355.0,
										157.0,
										29.5,
										22.0
									],
									"text": "276"
								}
							},
							{
								"box": {
									"id": "obj-39",
									"maxclass": "newobj",
									"numinlets": 3,
									"numoutlets": 3,
									"outlettype": [
										"bang",
										"bang",
										""
									],
									"patching_rect": [
										50.0,
										86.0,
										508.0,
										22.0
									],
									"text": "sel 0 1"
								}
							},
							{
								"box": {
									"id": "obj-36",
									"maxclass": "message",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										355.0,
										196.0,
										69.0,
										22.0
									],
									"text": "setwidth $1"
								}
							},
							{
								"box": {
									"comment": "",
									"id": "obj-47",
									"index": 1,
									"maxclass": "inlet",
									"numinlets": 0,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										50.0,
										40.0,
										30.0,
										30.0
									]
								}
							},
							{
								"box": {
									"comment": "",
									"id": "obj-51",
									"index": 1,
									"maxclass": "outlet",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										50.0,
										235.0,
										30.0,
										30.0
									]
								}
							},
							{
								"box": {
									"comment": "",
									"id": "obj-52",
									"index": 2,
									"maxclass": "outlet",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										355.0,
										235.0,
										30.0,
										30.0
									]
								}
							},
							{
								"box": {
									"comment": "",
									"id": "obj-53",
									"index": 3,
									"maxclass": "outlet",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										452.0,
										235.0,
										30.0,
										30.0
									]
								}
							}
						],
						"lines": [
							{
								"patchline": {
									"destination": [
										"obj-53",
										0
									],
									"source": [
										"obj-1",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-51",
										0
									],
									"source": [
										"obj-17",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-1",
										0
									],
									"source": [
										"obj-2",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-1",
										0
									],
									"source": [
										"obj-3",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-17",
										0
									],
									"source": [
										"obj-32",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-52",
										0
									],
									"source": [
										"obj-36",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-2",
										0
									],
									"midpoints": [
										59.5,
										139.5,
										461.5,
										139.5
									],
									"order": 0,
									"source": [
										"obj-39",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-3",
										0
									],
									"order": 0,
									"source": [
										"obj-39",
										1
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-32",
										0
									],
									"midpoints": [
										59.5,
										139.5,
										59.5,
										139.5
									],
									"order": 2,
									"source": [
										"obj-39",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-41",
										0
									],
									"order": 2,
									"source": [
										"obj-39",
										1
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-42",
										0
									],
									"midpoints": [
										59.5,
										139.5,
										364.5,
										139.5
									],
									"order": 1,
									"source": [
										"obj-39",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-43",
										0
									],
									"order": 1,
									"source": [
										"obj-39",
										1
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-17",
										0
									],
									"source": [
										"obj-41",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-36",
										0
									],
									"source": [
										"obj-42",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-36",
										0
									],
									"source": [
										"obj-43",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-39",
										0
									],
									"source": [
										"obj-47",
										0
									]
								}
							}
						],
						"saved_attribute_attributes": {
							"default_plcolor": {
								"expression": ""
							}
						}
					},
					"patching_rect": [
						162.0,
						233.0,
						71.0,
						20.0
					],
					"saved_attribute_attributes": {
						"default_plcolor": {
							"expression": ""
						}
					},
					"text": "p UiScripting"
				}
			},
			{
				"box": {
					"color": [
						1.0,
						0.694117647058824,
						0.0,
						1.0
					],
					"id": "obj-37",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patcher": {
						"fileversion": 1,
						"appversion": {
							"major": 9,
							"minor": 0,
							"revision": 8,
							"architecture": "x64",
							"modernui": 1
						},
						"classnamespace": "box",
						"rect": [
							317.0,
							99.0,
							382.0,
							581.0
						],
						"gridsize": [
							15.0,
							15.0
						],
						"boxes": [
							{
								"box": {
									"id": "obj-18",
									"maxclass": "newobj",
									"numinlets": 1,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										81.0,
										380.0,
										109.0,
										22.0
									],
									"text": "prepend bgoncolor"
								}
							},
							{
								"box": {
									"id": "obj-7",
									"maxclass": "message",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										234.0,
										221.0,
										75.0,
										22.0
									],
									"text": "\"Control On\""
								}
							},
							{
								"box": {
									"id": "obj-8",
									"maxclass": "message",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										221.0,
										260.0,
										75.0,
										22.0
									],
									"text": "\"Control Off\""
								}
							},
							{
								"box": {
									"id": "obj-11",
									"maxclass": "newobj",
									"numinlets": 3,
									"numoutlets": 3,
									"outlettype": [
										"bang",
										"bang",
										""
									],
									"patching_rect": [
										221.0,
										182.0,
										44.0,
										22.0
									],
									"text": "sel 0 1"
								}
							},
							{
								"box": {
									"id": "obj-6",
									"maxclass": "newobj",
									"numinlets": 1,
									"numoutlets": 2,
									"outlettype": [
										"bang",
										"int"
									],
									"patching_rect": [
										52.0,
										58.0,
										29.5,
										22.0
									],
									"text": "t b i"
								}
							},
							{
								"box": {
									"id": "obj-5",
									"maxclass": "newobj",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										"int"
									],
									"patching_rect": [
										121.0,
										97.0,
										29.5,
										22.0
									],
									"text": "i"
								}
							},
							{
								"box": {
									"id": "obj-4",
									"maxclass": "newobj",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										"int"
									],
									"patching_rect": [
										63.0,
										97.0,
										29.5,
										22.0
									],
									"text": "+ 1"
								}
							},
							{
								"box": {
									"id": "obj-3",
									"maxclass": "newobj",
									"numinlets": 2,
									"numoutlets": 2,
									"outlettype": [
										"",
										""
									],
									"patching_rect": [
										63.0,
										136.0,
										77.0,
										22.0
									],
									"text": "gate 2 1"
								}
							},
							{
								"box": {
									"id": "obj-2",
									"maxclass": "newobj",
									"numinlets": 1,
									"numoutlets": 3,
									"outlettype": [
										"bang",
										"int",
										"int"
									],
									"patching_rect": [
										20.0,
										19.0,
										83.0,
										22.0
									],
									"text": "live.thisdevice"
								}
							},
							{
								"box": {
									"id": "obj-1",
									"maxclass": "newobj",
									"numinlets": 1,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										63.0,
										302.0,
										19.0,
										22.0
									],
									"text": "t l"
								}
							},
							{
								"box": {
									"id": "obj-39",
									"maxclass": "message",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										76.0,
										221.0,
										128.0,
										22.0
									],
									"text": "\"Control On (Inactive)\""
								}
							},
							{
								"box": {
									"id": "obj-38",
									"maxclass": "newobj",
									"numinlets": 1,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										121.0,
										458.0,
										140.0,
										22.0
									],
									"text": "prepend activebgoncolor"
								}
							},
							{
								"box": {
									"id": "obj-31",
									"maxclass": "newobj",
									"numinlets": 1,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										100.0,
										419.0,
										127.0,
										22.0
									],
									"text": "prepend activebgcolor"
								}
							},
							{
								"box": {
									"id": "obj-29",
									"maxclass": "newobj",
									"numinlets": 1,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										63.0,
										341.0,
										95.0,
										22.0
									],
									"text": "prepend bgcolor"
								}
							},
							{
								"box": {
									"id": "obj-19",
									"maxclass": "message",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										63.0,
										260.0,
										75.0,
										22.0
									],
									"text": "\"Control Off\""
								}
							},
							{
								"box": {
									"id": "obj-12",
									"maxclass": "newobj",
									"numinlets": 3,
									"numoutlets": 3,
									"outlettype": [
										"bang",
										"bang",
										""
									],
									"patching_rect": [
										63.0,
										182.0,
										44.0,
										22.0
									],
									"text": "sel 0 1"
								}
							},
							{
								"box": {
									"comment": "",
									"id": "obj-9",
									"index": 1,
									"maxclass": "inlet",
									"numinlets": 0,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										121.0,
										15.0,
										30.0,
										30.0
									]
								}
							},
							{
								"box": {
									"comment": "",
									"id": "obj-10",
									"index": 1,
									"maxclass": "outlet",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										63.0,
										505.0,
										30.0,
										30.0
									]
								}
							}
						],
						"lines": [
							{
								"patchline": {
									"destination": [
										"obj-18",
										0
									],
									"order": 2,
									"source": [
										"obj-1",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-29",
										0
									],
									"order": 3,
									"source": [
										"obj-1",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-31",
										0
									],
									"order": 1,
									"source": [
										"obj-1",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-38",
										0
									],
									"order": 0,
									"source": [
										"obj-1",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-7",
										0
									],
									"source": [
										"obj-11",
										1
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-8",
										0
									],
									"source": [
										"obj-11",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-19",
										0
									],
									"source": [
										"obj-12",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-39",
										0
									],
									"source": [
										"obj-12",
										1
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-10",
										0
									],
									"source": [
										"obj-18",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-1",
										0
									],
									"source": [
										"obj-19",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-6",
										0
									],
									"source": [
										"obj-2",
										1
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-10",
										0
									],
									"source": [
										"obj-29",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-11",
										0
									],
									"source": [
										"obj-3",
										1
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-12",
										0
									],
									"source": [
										"obj-3",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-10",
										0
									],
									"source": [
										"obj-31",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-10",
										0
									],
									"source": [
										"obj-38",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-1",
										0
									],
									"source": [
										"obj-39",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-3",
										0
									],
									"source": [
										"obj-4",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-3",
										1
									],
									"source": [
										"obj-5",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-4",
										0
									],
									"source": [
										"obj-6",
										1
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-5",
										0
									],
									"source": [
										"obj-6",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-1",
										0
									],
									"source": [
										"obj-7",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-1",
										0
									],
									"source": [
										"obj-8",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-5",
										0
									],
									"source": [
										"obj-9",
										0
									]
								}
							}
						],
						"saved_attribute_attributes": {
							"default_plcolor": {
								"expression": ""
							}
						}
					},
					"patching_rect": [
						166.0,
						179.0,
						122.0,
						20.0
					],
					"saved_attribute_attributes": {
						"default_plcolor": {
							"expression": ""
						}
					},
					"text": "p SideChainActiveColor"
				}
			},
			{
				"box": {
					"id": "obj-16",
					"maxclass": "newobj",
					"numinlets": 4,
					"numoutlets": 4,
					"outlettype": [
						"signal",
						"signal",
						"signal",
						"signal"
					],
					"patching_rect": [
						45.0,
						113.0,
						109.0,
						20.0
					],
					"text": "plugin~ 1 2 3 4"
				}
			},
			{
				"box": {
					"id": "obj-22",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						""
					],
					"patching_rect": [
						162.0,
						323.0,
						62.0,
						20.0
					],
					"save": [
						"#N",
						"thispatcher",
						";",
						"#Q",
						"end",
						";"
					],
					"text": "thispatcher"
				}
			},
			{
				"box": {
					"id": "obj-31",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": [
						"bang",
						"int",
						"int"
					],
					"patching_rect": [
						188.0,
						293.0,
						77.0,
						20.0
					],
					"text": "live.thisdevice"
				}
			},
			{
				"box": {
					"id": "obj-23",
					"maxclass": "live.line",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						31.0,
						143.0,
						5.0,
						163.0
					]
				}
			},
			{
				"box": {
					"activebgcolor": [
						0.717647058823529,
						0.717647058823529,
						0.717647058823529,
						0.0
					],
					"activebgoncolor": [
						0.717647058823529,
						0.717647058823529,
						0.717647058823529,
						0.0
					],
					"bgcolor": [
						0.717647058823529,
						0.717647058823529,
						0.717647058823529,
						0.0
					],
					"bgoncolor": [
						0.717647058823529,
						0.717647058823529,
						0.717647058823529,
						0.0
					],
					"bordercolor": [
						0.717647058823529,
						0.717647058823529,
						0.717647058823529,
						0.0
					],
					"focusbordercolor": [
						0.717647058823529,
						0.717647058823529,
						0.717647058823529,
						0.0
					],
					"id": "obj-24",
					"ignoreclick": 1,
					"maxclass": "live.text",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						""
					],
					"parameter_enable": 1,
					"patching_rect": [
						6.0,
						143.0,
						15.0,
						74.0
					],
					"pictures": [
						"audio-rg.svg",
						"audio-rg.svg"
					],
					"remapsvgcolors": 1,
					"saved_attribute_attributes": {
						"activebgcolor": {
							"expression": ""
						},
						"activebgoncolor": {
							"expression": ""
						},
						"bgcolor": {
							"expression": ""
						},
						"bgoncolor": {
							"expression": ""
						},
						"bordercolor": {
							"expression": ""
						},
						"focusbordercolor": {
							"expression": ""
						},
						"textcolor": {
							"expression": "themecolor.live_control_fg_off"
						},
						"textoffcolor": {
							"expression": "themecolor.live_control_fg_off"
						},
						"valueof": {
							"parameter_enum": [
								"val1",
								"val2"
							],
							"parameter_invisible": 2,
							"parameter_longname": "live.text",
							"parameter_mmax": 1,
							"parameter_modmode": 0,
							"parameter_shortname": "live.text",
							"parameter_type": 2
						}
					},
					"textcolor": [
						0.0,
						0.0,
						0.0,
						1.0
					],
					"textoffcolor": [
						0.0,
						0.0,
						0.0,
						1.0
					],
					"usepicture": 1,
					"usesvgviewbox": 1,
					"varname": "live.text"
				}
			},
			{
				"box": {
					"activebgoncolor": [
						0.776470588235294,
						0.776470588235294,
						0.776470588235294,
						1.0
					],
					"annotation": "This button shows/hides the sidechain routing  panel.",
					"annotation_name": "Sidechain routing panel",
					"automation": "Closed",
					"automationon": "Open",
					"bgoncolor": [
						0.776470588235294,
						0.776470588235294,
						0.776470588235294,
						1.0
					],
					"fontname": "Ableton Sans Book",
					"fontsize": 9.17,
					"id": "obj-25",
					"lcdcolor": [
						0.0,
						0.0,
						0.0,
						1.0
					],
					"maxclass": "live.text",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						""
					],
					"outputmode": 1,
					"parameter_enable": 1,
					"patching_rect": [
						166.0,
						208.0,
						15.0,
						15.0
					],
					"pictures": [
						"sr-arrow-down-11x11.svg",
						"sr-arrow-right-11x11.svg"
					],
					"remapsvgcolors": 1,
					"rounded": 15.0,
					"saved_attribute_attributes": {
						"activebgoncolor": {
							"expression": "themecolor.live_control_bg"
						},
						"activetextoncolor": {
							"expression": "themecolor.live_control_text_selection"
						},
						"bgoncolor": {
							"expression": "themecolor.live_control_bg"
						},
						"lcdcolor": {
							"expression": "themecolor.live_control_fg"
						},
						"textcolor": {
							"expression": "themecolor.live_control_text_zombie"
						},
						"valueof": {
							"parameter_annotation_name": "Sidechain routing panel",
							"parameter_enum": [
								"Closed",
								"Open"
							],
							"parameter_info": "This button shows/hides the sidechain routing  panel.",
							"parameter_initial": [
								0
							],
							"parameter_invisible": 1,
							"parameter_linknames": 1,
							"parameter_longname": "ShowMod",
							"parameter_mmax": 1,
							"parameter_modmode": 0,
							"parameter_shortname": "Mappings",
							"parameter_type": 2
						}
					},
					"text": "I/O",
					"textcolor": [
						0.337254901960784,
						0.337254901960784,
						0.337254901960784,
						1.0
					],
					"texton": "I/O",
					"usepicture": 1,
					"usesvgviewbox": 1,
					"varname": "ShowMod"
				}
			},
			{
				"box": {
					"bgmode": 0,
					"border": 0,
					"clickthrough": 1,
					"embed": 1,
					"enablehscroll": 0,
					"enablevscroll": 0,
					"id": "obj-14",
					"lockeddragscroll": 0,
					"lockedsize": 0,
					"maxclass": "bpatcher",
					"name": "efsc.maxpat",
					"numinlets": 4,
					"numoutlets": 3,
					"offset": [
						0.0,
						0.0
					],
					"outlettype": [
						"signal",
						"signal",
						""
					],
					"patcher": {
						"fileversion": 1,
						"appversion": {
							"major": 9,
							"minor": 0,
							"revision": 8,
							"architecture": "x64",
							"modernui": 1
						},
						"classnamespace": "box",
						"rect": [
							862.0,
							485.0,
							854.0,
							431.0
						],
						"openinpresentation": 1,
						"gridsize": [
							15.0,
							15.0
						],
						"boxes": [
							{
								"box": {
									"id": "obj-19",
									"maxclass": "newobj",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										461.0,
										73.0,
										29.5,
										22.0
									],
									"text": "pak"
								}
							},
							{
								"box": {
									"id": "obj-16",
									"maxclass": "newobj",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										"int"
									],
									"patching_rect": [
										461.0,
										97.0,
										29.5,
										22.0
									],
									"text": "&&"
								}
							},
							{
								"box": {
									"id": "obj-13",
									"maxclass": "newobj",
									"numinlets": 1,
									"numoutlets": 3,
									"outlettype": [
										"bang",
										"int",
										"int"
									],
									"patching_rect": [
										439.0,
										34.0,
										83.0,
										22.0
									],
									"text": "live.thisdevice"
								}
							},
							{
								"box": {
									"id": "obj-12",
									"maxclass": "newobj",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										333.0,
										186.0,
										55.0,
										22.0
									],
									"text": "pak 0. 0."
								}
							},
							{
								"box": {
									"id": "obj-10",
									"maxclass": "newobj",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										"float"
									],
									"patching_rect": [
										333.0,
										225.0,
										29.5,
										22.0
									],
									"text": "* 0."
								}
							},
							{
								"box": {
									"id": "obj-9",
									"maxclass": "live.line",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										1000.0,
										273.0,
										6.0,
										58.0
									],
									"presentation": 1,
									"presentation_rect": [
										102.0,
										2.0,
										5.0,
										163.0
									]
								}
							},
							{
								"box": {
									"comment": "",
									"id": "obj-2",
									"index": 3,
									"maxclass": "outlet",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										397.0,
										34.0,
										30.0,
										30.0
									]
								}
							},
							{
								"box": {
									"id": "obj-18",
									"linecolor": [
										0.219607843137255,
										0.219607843137255,
										0.219607843137255,
										1.0
									],
									"maxclass": "live.line",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										873.0,
										301.0,
										92.0,
										21.0
									],
									"presentation": 1,
									"presentation_rect": [
										7.0,
										40.0,
										87.0,
										5.0
									],
									"saved_attribute_attributes": {
										"linecolor": {
											"expression": "themecolor.live_lcd_frame"
										}
									}
								}
							},
							{
								"box": {
									"id": "obj-32",
									"maxclass": "message",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										333.0,
										82.0,
										57.0,
										22.0
									],
									"text": "active $1"
								}
							},
							{
								"box": {
									"annotation": "Enable Sidechain to route audio from another track into the envelope follower.",
									"annotation_name": "Sidechain",
									"id": "obj-30",
									"maxclass": "live.text",
									"numinlets": 1,
									"numoutlets": 2,
									"outlettype": [
										"",
										""
									],
									"parameter_enable": 1,
									"patching_rect": [
										333.0,
										34.0,
										53.0,
										15.0
									],
									"presentation": 1,
									"presentation_rect": [
										11.0,
										5.0,
										79.0,
										15.0
									],
									"saved_attribute_attributes": {
										"valueof": {
											"parameter_annotation_name": "Sidechain",
											"parameter_enum": [
												"val1",
												"val2"
											],
											"parameter_info": "Enable Sidechain to route audio from another track into the envelope follower.",
											"parameter_initial": [
												0
											],
											"parameter_initial_enable": 1,
											"parameter_longname": "Sidechain",
											"parameter_mmax": 1,
											"parameter_modmode": 0,
											"parameter_shortname": "Sidechain",
											"parameter_type": 2
										}
									},
									"text": "Sidechain",
									"texton": "Sidechain",
									"varname": "live.text[1]"
								}
							},
							{
								"box": {
									"id": "obj-28",
									"maxclass": "live.comment",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										41.0,
										335.0,
										35.0,
										18.0
									],
									"presentation": 1,
									"presentation_rect": [
										0.0,
										82.0,
										35.0,
										18.0
									],
									"text": "Direct",
									"textjustification": 0
								}
							},
							{
								"box": {
									"id": "obj-24",
									"maxclass": "live.meter~",
									"numinlets": 1,
									"numoutlets": 2,
									"outlettype": [
										"float",
										"int"
									],
									"patching_rect": [
										160.0,
										286.0,
										8.0,
										47.0
									],
									"presentation": 1,
									"presentation_rect": [
										46.0,
										100.0,
										5.0,
										63.0
									],
									"slidercolor": [
										0.113725490196078,
										0.113725490196078,
										0.113725490196078,
										1.0
									]
								}
							},
							{
								"box": {
									"id": "obj-27",
									"maxclass": "live.meter~",
									"numinlets": 1,
									"numoutlets": 2,
									"outlettype": [
										"float",
										"int"
									],
									"patching_rect": [
										127.0,
										286.0,
										8.0,
										47.0
									],
									"presentation": 1,
									"presentation_rect": [
										40.0,
										100.0,
										5.0,
										63.0
									],
									"slidercolor": [
										0.113725490196078,
										0.113725490196078,
										0.113725490196078,
										1.0
									]
								}
							},
							{
								"box": {
									"annotation": "Mix between the direct input and the sidechained signal.",
									"annotation_name": "Sidechain Mix",
									"id": "obj-22",
									"maxclass": "live.dial",
									"numinlets": 1,
									"numoutlets": 2,
									"outlettype": [
										"",
										"float"
									],
									"parameter_enable": 1,
									"patching_rect": [
										333.0,
										121.0,
										41.0,
										48.0
									],
									"presentation": 1,
									"presentation_rect": [
										56.0,
										116.0,
										41.0,
										48.0
									],
									"saved_attribute_attributes": {
										"valueof": {
											"parameter_annotation_name": "Sidechain Mix",
											"parameter_info": "Mix between the direct input and the sidechained signal.",
											"parameter_longname": "Mix",
											"parameter_mmax": 100.0,
											"parameter_modmode": 2,
											"parameter_shortname": "Mix",
											"parameter_type": 0,
											"parameter_unitstyle": 5
										}
									},
									"varname": "live.dial"
								}
							},
							{
								"box": {
									"comment": "",
									"id": "obj-21",
									"index": 2,
									"maxclass": "outlet",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										333.0,
										303.0,
										30.0,
										30.0
									]
								}
							},
							{
								"box": {
									"comment": "",
									"id": "obj-20",
									"index": 1,
									"maxclass": "outlet",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										214.0,
										303.0,
										30.0,
										30.0
									]
								}
							},
							{
								"box": {
									"comment": "",
									"id": "obj-14",
									"index": 4,
									"maxclass": "inlet",
									"numinlets": 0,
									"numoutlets": 1,
									"outlettype": [
										"signal"
									],
									"patching_rect": [
										154.3,
										34.0,
										30.0,
										30.0
									]
								}
							},
							{
								"box": {
									"comment": "",
									"id": "obj-17",
									"index": 3,
									"maxclass": "inlet",
									"numinlets": 0,
									"numoutlets": 1,
									"outlettype": [
										"signal"
									],
									"patching_rect": [
										121.3,
										34.0,
										30.0,
										30.0
									]
								}
							},
							{
								"box": {
									"color": [
										0.0,
										0.694117647058824,
										1.0,
										1.0
									],
									"id": "obj-6",
									"maxclass": "newobj",
									"numinlets": 5,
									"numoutlets": 2,
									"outlettype": [
										"signal",
										"signal"
									],
									"patching_rect": [
										214.0,
										264.0,
										137.66666666666669,
										22.0
									],
									"text": "M4L.bal2~"
								}
							},
							{
								"box": {
									"comment": "",
									"id": "obj-5",
									"index": 2,
									"maxclass": "inlet",
									"numinlets": 0,
									"numoutlets": 1,
									"outlettype": [
										"signal"
									],
									"patching_rect": [
										68.3,
										34.0,
										30.0,
										30.0
									]
								}
							},
							{
								"box": {
									"comment": "",
									"id": "obj-4",
									"index": 1,
									"maxclass": "inlet",
									"numinlets": 0,
									"numoutlets": 1,
									"outlettype": [
										"signal"
									],
									"patching_rect": [
										35.3,
										34.0,
										30.0,
										30.0
									]
								}
							},
							{
								"box": {
									"id": "obj-11",
									"maxclass": "live.comment",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										125.0,
										335.0,
										28.0,
										18.0
									],
									"presentation": 1,
									"presentation_rect": [
										35.0,
										82.0,
										28.0,
										18.0
									],
									"text": "S.C. ",
									"textjustification": 0
								}
							},
							{
								"box": {
									"id": "obj-1",
									"maxclass": "live.comment",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										870.0,
										272.0,
										56.0,
										18.0
									],
									"presentation": 1,
									"presentation_rect": [
										20.0,
										23.0,
										56.0,
										18.0
									],
									"saved_attribute_attributes": {
										"textcolor": {
											"expression": "themecolor.live_lcd_control_fg_zombie"
										}
									},
									"text": "Audio From",
									"textcolor": [
										0.447058823529412,
										0.447058823529412,
										0.447058823529412,
										1.0
									],
									"textjustification": 0
								}
							},
							{
								"box": {
									"id": "obj-8",
									"maxclass": "live.meter~",
									"numinlets": 1,
									"numoutlets": 2,
									"outlettype": [
										"float",
										"int"
									],
									"patching_rect": [
										41.0,
										286.0,
										8.0,
										47.0
									],
									"presentation": 1,
									"presentation_rect": [
										13.0,
										100.0,
										5.0,
										63.0
									],
									"slidercolor": [
										0.113725490196078,
										0.113725490196078,
										0.113725490196078,
										1.0
									]
								}
							},
							{
								"box": {
									"id": "obj-7",
									"maxclass": "live.meter~",
									"numinlets": 1,
									"numoutlets": 2,
									"outlettype": [
										"float",
										"int"
									],
									"patching_rect": [
										74.0,
										286.0,
										8.0,
										47.0
									],
									"presentation": 1,
									"presentation_rect": [
										19.0,
										100.0,
										5.0,
										63.0
									],
									"slidercolor": [
										0.113725490196078,
										0.113725490196078,
										0.113725490196078,
										1.0
									]
								}
							},
							{
								"box": {
									"allowdrag": 0,
									"annotation": "Selects the input channel",
									"bgcolor": [
										1,
										1,
										1,
										0
									],
									"bgfillcolor_angle": 270,
									"bgfillcolor_autogradient": 0,
									"bgfillcolor_color": [
										1,
										1,
										1,
										0
									],
									"bgfillcolor_color1": [
										0.376471,
										0.384314,
										0.4,
										1
									],
									"bgfillcolor_color2": [
										0.290196,
										0.309804,
										0.301961,
										1
									],
									"bgfillcolor_proportion": 0.39,
									"bgfillcolor_type": "color",
									"blanksym": "",
									"fontname": "Ableton Sans Medium Regular",
									"fontsize": 9.5,
									"hint": "",
									"id": "obj-47",
									"items": "<none>",
									"maxclass": "umenu",
									"numinlets": 1,
									"numoutlets": 3,
									"outlettype": [
										"int",
										"",
										""
									],
									"parameter_enable": 0,
									"patching_rect": [
										724.0,
										272.0,
										84.0,
										20.0
									],
									"presentation": 1,
									"presentation_rect": [
										4.0,
										58.0,
										94.0,
										20.0
									],
									"saved_attribute_attributes": {
										"textcolor": {
											"expression": "themecolor.live_lcd_control_fg_zombie"
										}
									},
									"textcolor": [
										0.447058823529412,
										0.447058823529412,
										0.447058823529412,
										1.0
									]
								}
							},
							{
								"box": {
									"allowdrag": 0,
									"annotation": "Selects an audio source",
									"bgcolor": [
										1,
										1,
										1,
										0
									],
									"bgfillcolor_angle": 270,
									"bgfillcolor_autogradient": 0,
									"bgfillcolor_color": [
										1,
										1,
										1,
										0
									],
									"bgfillcolor_color1": [
										0.376471,
										0.384314,
										0.4,
										1
									],
									"bgfillcolor_color2": [
										0.290196,
										0.309804,
										0.301961,
										1
									],
									"bgfillcolor_proportion": 0.39,
									"bgfillcolor_type": "color",
									"fontname": "Ableton Sans Medium Regular",
									"fontsize": 9.5,
									"hint": "",
									"id": "obj-15",
									"items": [
										"Ext. In",
										",",
										"1-03_Dancing Sparkle",
										",",
										"NATIVIZE",
										",",
										"3-3 - dancing sparkle - raw backing",
										",",
										"4-d. violin",
										",",
										"Bilateral LFO",
										",",
										"6-c. white-noise-ambiance",
										",",
										"7-b. soundscape",
										",",
										"MCP Devicev2",
										",",
										"10-dancing_sparkle_pitch_signal_v12",
										",",
										"Synths",
										",",
										"onset_signal",
										",",
										"articulation_signal",
										",",
										"notechange_signal",
										",",
										"pitch_vibrato_signal",
										",",
										"vibrato_intensity_signal",
										",",
										"17-Audio",
										",",
										"A-Reverb",
										",",
										"B-Delay",
										",",
										"Main",
										",",
										"No Input"
									],
									"maxclass": "umenu",
									"numinlets": 1,
									"numoutlets": 3,
									"outlettype": [
										"int",
										"",
										""
									],
									"parameter_enable": 0,
									"patching_rect": [
										633.0,
										272.0,
										84.0,
										20.0
									],
									"presentation": 1,
									"presentation_rect": [
										4.0,
										42.0,
										95.0,
										20.0
									],
									"saved_attribute_attributes": {
										"textcolor": {
											"expression": "themecolor.live_lcd_control_fg_zombie"
										}
									},
									"textcolor": [
										0.447058823529412,
										0.447058823529412,
										0.447058823529412,
										1.0
									]
								}
							},
							{
								"box": {
									"angle": 270.0,
									"bgcolor": [
										0.113725490196078,
										0.113725490196078,
										0.113725490196078,
										1.0
									],
									"id": "obj-3",
									"maxclass": "panel",
									"mode": 0,
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										870.0,
										272.0,
										98.0,
										61.0
									],
									"presentation": 1,
									"presentation_rect": [
										3.0,
										23.0,
										95.0,
										55.0
									],
									"proportion": 0.39,
									"rounded": 4,
									"saved_attribute_attributes": {
										"bgfillcolor": {
											"expression": "themecolor.live_lcd_bg"
										}
									}
								}
							},
							{
								"box": {
									"id": "obj-40",
									"maxclass": "message",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										461.0,
										197.0,
										152.0,
										22.0
									],
									"text": "\"LCD Text / Icon (Inactive)\""
								}
							},
							{
								"box": {
									"id": "obj-39",
									"maxclass": "newobj",
									"numinlets": 3,
									"numoutlets": 3,
									"outlettype": [
										"bang",
										"bang",
										""
									],
									"patching_rect": [
										461.0,
										126.0,
										44.0,
										22.0
									],
									"text": "sel 0 1"
								}
							},
							{
								"box": {
									"id": "obj-38",
									"maxclass": "newobj",
									"numinlets": 1,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										461.0,
										236.0,
										101.0,
										22.0
									],
									"text": "prepend textcolor"
								}
							},
							{
								"box": {
									"id": "obj-34",
									"maxclass": "message",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										474.0,
										158.0,
										99.0,
										22.0
									],
									"text": "\"LCD Text / Icon\""
								}
							},
							{
								"box": {
									"id": "obj-23",
									"maxclass": "newobj",
									"numinlets": 1,
									"numoutlets": 3,
									"outlettype": [
										"bang",
										"int",
										"int"
									],
									"patching_rect": [
										633.0,
										117.0,
										83.0,
										22.0
									],
									"text": "live.thisdevice"
								}
							},
							{
								"box": {
									"id": "obj-25",
									"maxclass": "message",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										633.0,
										156.0,
										146.0,
										22.0
									],
									"text": "port audio_inputs, index 1"
								}
							},
							{
								"box": {
									"color": [
										1.0,
										0.694117647058824,
										0.0,
										1.0
									],
									"id": "obj-45",
									"maxclass": "newobj",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										"clear"
									],
									"patcher": {
										"fileversion": 1,
										"appversion": {
											"major": 9,
											"minor": 0,
											"revision": 8,
											"architecture": "x64",
											"modernui": 1
										},
										"classnamespace": "box",
										"rect": [
											134.0,
											172.0,
											321.0,
											265.0
										],
										"gridsize": [
											15.0,
											15.0
										],
										"boxes": [
											{
												"box": {
													"id": "obj-29",
													"maxclass": "newobj",
													"numinlets": 1,
													"numoutlets": 1,
													"outlettype": [
														""
													],
													"patching_rect": [
														30.0,
														66.0,
														72.0,
														22.0
													],
													"text": "prepend set"
												}
											},
											{
												"box": {
													"id": "obj-25",
													"maxclass": "newobj",
													"numinlets": 1,
													"numoutlets": 1,
													"outlettype": [
														""
													],
													"patching_rect": [
														158.0,
														144.0,
														96.0,
														22.0
													],
													"text": "prepend append"
												}
											},
											{
												"box": {
													"id": "obj-26",
													"maxclass": "newobj",
													"numinlets": 1,
													"numoutlets": 1,
													"outlettype": [
														""
													],
													"patching_rect": [
														158.0,
														105.0,
														25.0,
														22.0
													],
													"text": "iter"
												}
											},
											{
												"box": {
													"id": "obj-27",
													"maxclass": "newobj",
													"numinlets": 1,
													"numoutlets": 2,
													"outlettype": [
														"",
														"clear"
													],
													"patching_rect": [
														158.0,
														66.0,
														47.0,
														22.0
													],
													"text": "t l clear"
												}
											},
											{
												"box": {
													"comment": "",
													"id": "obj-33",
													"index": 1,
													"maxclass": "inlet",
													"numinlets": 0,
													"numoutlets": 1,
													"outlettype": [
														""
													],
													"patching_rect": [
														30.0,
														19.0,
														30.0,
														30.0
													]
												}
											},
											{
												"box": {
													"comment": "",
													"id": "obj-34",
													"index": 2,
													"maxclass": "inlet",
													"numinlets": 0,
													"numoutlets": 1,
													"outlettype": [
														""
													],
													"patching_rect": [
														158.0,
														19.0,
														30.0,
														30.0
													]
												}
											},
											{
												"box": {
													"comment": "",
													"id": "obj-35",
													"index": 1,
													"maxclass": "outlet",
													"numinlets": 1,
													"numoutlets": 0,
													"patching_rect": [
														30.0,
														209.0,
														30.0,
														30.0
													]
												}
											}
										],
										"lines": [
											{
												"patchline": {
													"destination": [
														"obj-35",
														0
													],
													"source": [
														"obj-25",
														0
													]
												}
											},
											{
												"patchline": {
													"destination": [
														"obj-25",
														0
													],
													"source": [
														"obj-26",
														0
													]
												}
											},
											{
												"patchline": {
													"destination": [
														"obj-26",
														0
													],
													"source": [
														"obj-27",
														0
													]
												}
											},
											{
												"patchline": {
													"destination": [
														"obj-35",
														0
													],
													"source": [
														"obj-27",
														1
													]
												}
											},
											{
												"patchline": {
													"destination": [
														"obj-35",
														0
													],
													"source": [
														"obj-29",
														0
													]
												}
											},
											{
												"patchline": {
													"destination": [
														"obj-29",
														0
													],
													"source": [
														"obj-33",
														0
													]
												}
											},
											{
												"patchline": {
													"destination": [
														"obj-27",
														0
													],
													"source": [
														"obj-34",
														0
													]
												}
											}
										],
										"saved_attribute_attributes": {
											"default_plcolor": {
												"expression": ""
											}
										}
									},
									"patching_rect": [
										724.0,
										236.0,
										49.0,
										22.0
									],
									"saved_attribute_attributes": {
										"default_plcolor": {
											"expression": ""
										}
									},
									"text": "p Menu"
								}
							},
							{
								"box": {
									"color": [
										1.0,
										0.694117647058824,
										0.0,
										1.0
									],
									"id": "obj-46",
									"maxclass": "newobj",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										"clear"
									],
									"patcher": {
										"fileversion": 1,
										"appversion": {
											"major": 9,
											"minor": 0,
											"revision": 8,
											"architecture": "x64",
											"modernui": 1
										},
										"classnamespace": "box",
										"rect": [
											134.0,
											172.0,
											314.0,
											292.0
										],
										"gridsize": [
											15.0,
											15.0
										],
										"boxes": [
											{
												"box": {
													"id": "obj-29",
													"maxclass": "newobj",
													"numinlets": 1,
													"numoutlets": 1,
													"outlettype": [
														""
													],
													"patching_rect": [
														30.0,
														66.0,
														72.0,
														22.0
													],
													"text": "prepend set"
												}
											},
											{
												"box": {
													"id": "obj-25",
													"maxclass": "newobj",
													"numinlets": 1,
													"numoutlets": 1,
													"outlettype": [
														""
													],
													"patching_rect": [
														158.0,
														144.0,
														96.0,
														22.0
													],
													"text": "prepend append"
												}
											},
											{
												"box": {
													"id": "obj-26",
													"maxclass": "newobj",
													"numinlets": 1,
													"numoutlets": 1,
													"outlettype": [
														""
													],
													"patching_rect": [
														158.0,
														105.0,
														25.0,
														22.0
													],
													"text": "iter"
												}
											},
											{
												"box": {
													"id": "obj-27",
													"maxclass": "newobj",
													"numinlets": 1,
													"numoutlets": 2,
													"outlettype": [
														"",
														"clear"
													],
													"patching_rect": [
														158.0,
														66.0,
														47.0,
														22.0
													],
													"text": "t l clear"
												}
											},
											{
												"box": {
													"comment": "",
													"id": "obj-33",
													"index": 1,
													"maxclass": "inlet",
													"numinlets": 0,
													"numoutlets": 1,
													"outlettype": [
														""
													],
													"patching_rect": [
														30.0,
														19.0,
														30.0,
														30.0
													]
												}
											},
											{
												"box": {
													"comment": "",
													"id": "obj-34",
													"index": 2,
													"maxclass": "inlet",
													"numinlets": 0,
													"numoutlets": 1,
													"outlettype": [
														""
													],
													"patching_rect": [
														158.0,
														19.0,
														30.0,
														30.0
													]
												}
											},
											{
												"box": {
													"comment": "",
													"id": "obj-35",
													"index": 1,
													"maxclass": "outlet",
													"numinlets": 1,
													"numoutlets": 0,
													"patching_rect": [
														30.0,
														209.0,
														30.0,
														30.0
													]
												}
											}
										],
										"lines": [
											{
												"patchline": {
													"destination": [
														"obj-35",
														0
													],
													"source": [
														"obj-25",
														0
													]
												}
											},
											{
												"patchline": {
													"destination": [
														"obj-25",
														0
													],
													"source": [
														"obj-26",
														0
													]
												}
											},
											{
												"patchline": {
													"destination": [
														"obj-26",
														0
													],
													"source": [
														"obj-27",
														0
													]
												}
											},
											{
												"patchline": {
													"destination": [
														"obj-35",
														0
													],
													"source": [
														"obj-27",
														1
													]
												}
											},
											{
												"patchline": {
													"destination": [
														"obj-35",
														0
													],
													"source": [
														"obj-29",
														0
													]
												}
											},
											{
												"patchline": {
													"destination": [
														"obj-29",
														0
													],
													"source": [
														"obj-33",
														0
													]
												}
											},
											{
												"patchline": {
													"destination": [
														"obj-27",
														0
													],
													"source": [
														"obj-34",
														0
													]
												}
											}
										],
										"saved_attribute_attributes": {
											"default_plcolor": {
												"expression": ""
											}
										}
									},
									"patching_rect": [
										633.0,
										236.0,
										49.0,
										22.0
									],
									"saved_attribute_attributes": {
										"default_plcolor": {
											"expression": ""
										}
									},
									"text": "p Menu"
								}
							},
							{
								"box": {
									"id": "obj-31",
									"maxclass": "newobj",
									"numinlets": 1,
									"numoutlets": 5,
									"outlettype": [
										"",
										"",
										"",
										"",
										""
									],
									"patching_rect": [
										633.0,
										195.0,
										180.33333333333337,
										22.0
									],
									"text": "live.routing"
								}
							},
							{
								"box": {
									"id": "obj-74",
									"maxclass": "message",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										633.0,
										309.0,
										50.0,
										22.0
									],
									"text": "type $1"
								}
							},
							{
								"box": {
									"id": "obj-75",
									"maxclass": "message",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										724.0,
										309.0,
										67.0,
										22.0
									],
									"text": "channel $1"
								}
							}
						],
						"lines": [
							{
								"patchline": {
									"destination": [
										"obj-6",
										4
									],
									"source": [
										"obj-10",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-10",
										0
									],
									"source": [
										"obj-12",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-19",
										1
									],
									"source": [
										"obj-13",
										1
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-24",
										0
									],
									"order": 1,
									"source": [
										"obj-14",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-6",
										3
									],
									"order": 0,
									"source": [
										"obj-14",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-74",
										0
									],
									"source": [
										"obj-15",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-39",
										0
									],
									"source": [
										"obj-16",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-27",
										0
									],
									"order": 1,
									"source": [
										"obj-17",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-6",
										2
									],
									"order": 0,
									"source": [
										"obj-17",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-16",
										0
									],
									"source": [
										"obj-19",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-12",
										0
									],
									"source": [
										"obj-22",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-25",
										0
									],
									"source": [
										"obj-23",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-31",
										0
									],
									"source": [
										"obj-25",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-12",
										1
									],
									"order": 2,
									"source": [
										"obj-30",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-19",
										0
									],
									"order": 0,
									"source": [
										"obj-30",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-2",
										0
									],
									"order": 1,
									"source": [
										"obj-30",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-32",
										0
									],
									"order": 3,
									"source": [
										"obj-30",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-45",
										1
									],
									"source": [
										"obj-31",
										3
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-45",
										0
									],
									"source": [
										"obj-31",
										1
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-46",
										1
									],
									"source": [
										"obj-31",
										2
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-46",
										0
									],
									"source": [
										"obj-31",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-22",
										0
									],
									"order": 0,
									"source": [
										"obj-32",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-24",
										0
									],
									"order": 1,
									"source": [
										"obj-32",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-27",
										0
									],
									"order": 2,
									"source": [
										"obj-32",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-38",
										0
									],
									"source": [
										"obj-34",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-15",
										0
									],
									"order": 1,
									"source": [
										"obj-38",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-47",
										0
									],
									"order": 0,
									"source": [
										"obj-38",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-34",
										0
									],
									"source": [
										"obj-39",
										1
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-40",
										0
									],
									"source": [
										"obj-39",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-6",
										0
									],
									"order": 0,
									"source": [
										"obj-4",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-8",
										0
									],
									"order": 1,
									"source": [
										"obj-4",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-38",
										0
									],
									"source": [
										"obj-40",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-47",
										0
									],
									"source": [
										"obj-45",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-15",
										0
									],
									"source": [
										"obj-46",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-75",
										0
									],
									"source": [
										"obj-47",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-6",
										1
									],
									"order": 0,
									"source": [
										"obj-5",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-7",
										0
									],
									"order": 1,
									"source": [
										"obj-5",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-20",
										0
									],
									"source": [
										"obj-6",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-21",
										0
									],
									"source": [
										"obj-6",
										1
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-31",
										0
									],
									"midpoints": [
										642.5,
										341.0,
										830.0,
										341.0,
										830.0,
										184.0,
										642.5,
										184.0
									],
									"source": [
										"obj-74",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-31",
										0
									],
									"midpoints": [
										733.5,
										341.0,
										830.0,
										341.0,
										830.0,
										184.0,
										642.5,
										184.0
									],
									"source": [
										"obj-75",
										0
									]
								}
							}
						],
						"saved_attribute_attributes": {
							"default_plcolor": {
								"expression": ""
							}
						}
					},
					"patching_rect": [
						46.0,
						143.0,
						108.0,
						172.0
					],
					"varname": "sc",
					"viewvisibility": 1
				}
			},
			{
				"box": {
					"id": "obj-12",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						214.0,
						263.0,
						56.0,
						20.0
					],
					"saved_object_attributes": {
						"filename": "moveUi",
						"parameter_enable": 0
					},
					"text": "js moveUi"
				}
			},
			{
				"box": {
					"id": "obj-10",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						578.0,
						424.0,
						71.0,
						20.0
					],
					"text": "loadmess 0.5"
				}
			},
			{
				"box": {
					"bgmode": 0,
					"border": 0,
					"clickthrough": 0,
					"enablehscroll": 0,
					"enablevscroll": 0,
					"id": "obj-3",
					"lockeddragscroll": 0,
					"lockedsize": 0,
					"maxclass": "bpatcher",
					"name": "Abl.MapUi.maxpat",
					"numinlets": 3,
					"numoutlets": 7,
					"offset": [
						0.0,
						0.0
					],
					"outlettype": [
						"",
						"",
						"",
						"",
						"",
						"",
						""
					],
					"patching_rect": [
						338.0,
						462.0,
						225.0,
						20.0
					],
					"viewvisibility": 1
				}
			},
			{
				"box": {
					"bgmode": 0,
					"border": 0,
					"clickthrough": 0,
					"enablehscroll": 0,
					"enablevscroll": 0,
					"id": "obj-27",
					"lockeddragscroll": 0,
					"lockedsize": 0,
					"maxclass": "bpatcher",
					"name": "Abl.MultiMap.maxpat",
					"numinlets": 3,
					"numoutlets": 1,
					"offset": [
						0.0,
						0.0
					],
					"outlettype": [
						""
					],
					"patching_rect": [
						283.0,
						540.0,
						229.0,
						166.0
					],
					"varname": "multimap",
					"viewvisibility": 1
				}
			},
			{
				"box": {
					"id": "obj-35",
					"maxclass": "live.line",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						371.0,
						161.0,
						6.0,
						5.0
					]
				}
			},
			{
				"box": {
					"color": [
						0.0,
						1.0,
						0.694117647058824,
						1.0
					],
					"id": "obj-1",
					"maxclass": "newobj",
					"numinlets": 10,
					"numoutlets": 4,
					"outlettype": [
						"",
						"",
						"",
						""
					],
					"patching_rect": [
						304.0,
						490.0,
						327.25,
						20.0
					],
					"text": "poly~ Abl.Map"
				}
			},
			{
				"box": {
					"id": "obj-7",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						283.0,
						450.0,
						30.0,
						20.0
					],
					"text": "*~ 1."
				}
			},
			{
				"box": {
					"id": "obj-6",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						374.0,
						324.0,
						92.0,
						20.0
					],
					"text": "switch 2 1"
				}
			},
			{
				"box": {
					"color": [
						1.0,
						0.694117647058824,
						0.0,
						1.0
					],
					"id": "obj-21",
					"maxclass": "newobj",
					"numinlets": 0,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patcher": {
						"fileversion": 1,
						"appversion": {
							"major": 9,
							"minor": 0,
							"revision": 8,
							"architecture": "x64",
							"modernui": 1
						},
						"classnamespace": "box",
						"rect": [
							226.0,
							211.0,
							290.0,
							313.0
						],
						"gridsize": [
							15.0,
							15.0
						],
						"boxes": [
							{
								"box": {
									"id": "obj-13",
									"maxclass": "newobj",
									"numinlets": 1,
									"numoutlets": 4,
									"outlettype": [
										"int",
										"float",
										"int",
										"int"
									],
									"patching_rect": [
										39.0,
										33.0,
										61.0,
										22.0
									],
									"text": "dspstate~"
								}
							},
							{
								"box": {
									"id": "obj-53",
									"maxclass": "newobj",
									"numinlets": 1,
									"numoutlets": 3,
									"outlettype": [
										"",
										"int",
										"int"
									],
									"patching_rect": [
										53.0,
										111.0,
										48.0,
										22.0
									],
									"text": "change"
								}
							},
							{
								"box": {
									"id": "obj-32",
									"maxclass": "newobj",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										"float"
									],
									"patching_rect": [
										53.0,
										72.0,
										30.0,
										22.0
									],
									"text": "* 3."
								}
							},
							{
								"box": {
									"id": "obj-29",
									"maxclass": "message",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										53.0,
										150.0,
										70.0,
										22.0
									],
									"text": "samples $1"
								}
							},
							{
								"box": {
									"id": "obj-50",
									"maxclass": "message",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										167.0,
										150.0,
										57.0,
										22.0
									],
									"text": "active $1"
								}
							},
							{
								"box": {
									"id": "obj-21",
									"maxclass": "newobj",
									"numinlets": 1,
									"numoutlets": 3,
									"outlettype": [
										"bang",
										"int",
										"int"
									],
									"patching_rect": [
										135.0,
										111.0,
										83.0,
										22.0
									],
									"text": "live.thisdevice"
								}
							},
							{
								"box": {
									"comment": "to scope",
									"id": "obj-14",
									"index": 1,
									"maxclass": "outlet",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										53.0,
										219.0,
										30.0,
										30.0
									]
								}
							}
						],
						"lines": [
							{
								"patchline": {
									"destination": [
										"obj-32",
										0
									],
									"source": [
										"obj-13",
										1
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-50",
										0
									],
									"source": [
										"obj-21",
										1
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-14",
										0
									],
									"source": [
										"obj-29",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-53",
										0
									],
									"source": [
										"obj-32",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-14",
										0
									],
									"source": [
										"obj-50",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-29",
										0
									],
									"source": [
										"obj-53",
										0
									]
								}
							}
						],
						"saved_attribute_attributes": {
							"default_plcolor": {
								"expression": ""
							}
						}
					},
					"patching_rect": [
						69.0,
						378.0,
						62.0,
						20.0
					],
					"saved_attribute_attributes": {
						"default_plcolor": {
							"expression": ""
						}
					},
					"text": "p InitScope"
				}
			},
			{
				"box": {
					"activebgcolor": [
						0.156862745098039,
						0.156862745098039,
						0.156862745098039,
						0.0
					],
					"bgcolor": [
						0.156862745098039,
						0.156862745098039,
						0.156862745098039,
						0.0
					],
					"id": "obj-8",
					"line_width": 1.5,
					"maxclass": "live.scope~",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"bang"
					],
					"patching_rect": [
						46.0,
						478.0,
						88.0,
						56.0
					],
					"presentation": 1,
					"presentation_rect": [
						4.0,
						25.0,
						268.0,
						88.0
					],
					"range": [
						-0.05,
						1.05
					],
					"samples": 144000.0,
					"saved_attribute_attributes": {
						"activebgcolor": {
							"expression": ""
						},
						"bgcolor": {
							"expression": ""
						}
					}
				}
			},
			{
				"box": {
					"activebgcolor": [
						0.098039215686275,
						0.098039215686275,
						0.098039215686275,
						0.0
					],
					"activelinecolor": [
						0.219607843137255,
						0.219607843137255,
						0.219607843137255,
						1.0
					],
					"bgcolor": [
						0.098039215686275,
						0.098039215686275,
						0.098039215686275,
						0.0
					],
					"decay_time": 10.0,
					"id": "obj-20",
					"interval": 20.0,
					"maxclass": "live.scope~",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"bang"
					],
					"patching_rect": [
						46.0,
						414.0,
						88.0,
						56.0
					],
					"presentation": 1,
					"presentation_rect": [
						4.0,
						25.0,
						268.0,
						88.0
					],
					"range": [
						-0.05,
						1.0
					],
					"samples": 144000.0,
					"saved_attribute_attributes": {
						"activebgcolor": {
							"expression": ""
						},
						"activelinecolor": {
							"expression": "themecolor.live_lcd_frame"
						},
						"bgcolor": {
							"expression": ""
						}
					}
				}
			},
			{
				"box": {
					"id": "obj-40",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"int"
					],
					"patching_rect": [
						374.0,
						295.0,
						30.0,
						20.0
					],
					"text": "+ 1"
				}
			},
			{
				"box": {
					"id": "obj-13",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						""
					],
					"patching_rect": [
						283.0,
						718.0,
						62.0,
						20.0
					],
					"save": [
						"#N",
						"thispatcher",
						";",
						"#Q",
						"end",
						";"
					],
					"text": "thispatcher"
				}
			},
			{
				"box": {
					"color": [
						0.733333333333333,
						1.0,
						0.0,
						1.0
					],
					"id": "obj-5",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patcher": {
						"fileversion": 1,
						"appversion": {
							"major": 9,
							"minor": 0,
							"revision": 8,
							"architecture": "x64",
							"modernui": 1
						},
						"classnamespace": "box",
						"rect": [
							743.0,
							509.0,
							280.0,
							314.0
						],
						"gridsize": [
							15.0,
							15.0
						],
						"boxes": [
							{
								"box": {
									"id": "obj-1",
									"maxclass": "newobj",
									"numinlets": 1,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										31.0,
										66.0,
										54.0,
										22.0
									],
									"text": "deferlow"
								}
							},
							{
								"box": {
									"id": "obj-17",
									"maxclass": "newobj",
									"numinlets": 2,
									"numoutlets": 2,
									"outlettype": [
										"bang",
										""
									],
									"patching_rect": [
										31.0,
										105.0,
										36.0,
										22.0
									],
									"text": "sel 0"
								}
							},
							{
								"box": {
									"id": "obj-14",
									"maxclass": "message",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										31.0,
										183.0,
										114.0,
										22.0
									],
									"text": "edit 0 Main 6 Delay"
								}
							},
							{
								"box": {
									"id": "obj-13",
									"maxclass": "message",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										48.0,
										144.0,
										165.0,
										22.0
									],
									"text": "edit 0 Main 6 \"Delay Synced\""
								}
							},
							{
								"box": {
									"annotation": "",
									"comment": "(bool) free / sync",
									"id": "obj-10",
									"index": 1,
									"maxclass": "inlet",
									"numinlets": 0,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										31.0,
										19.0,
										30.0,
										30.0
									]
								}
							},
							{
								"box": {
									"id": "obj-2",
									"maxclass": "newobj",
									"numinlets": 1,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										31.0,
										222.0,
										64.0,
										22.0
									],
									"text": "live.banks"
								}
							}
						],
						"lines": [
							{
								"patchline": {
									"destination": [
										"obj-17",
										0
									],
									"source": [
										"obj-1",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-1",
										0
									],
									"source": [
										"obj-10",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-2",
										0
									],
									"source": [
										"obj-13",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-2",
										0
									],
									"source": [
										"obj-14",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-13",
										0
									],
									"source": [
										"obj-17",
										1
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-14",
										0
									],
									"source": [
										"obj-17",
										0
									]
								}
							}
						],
						"saved_attribute_attributes": {
							"default_plcolor": {
								"expression": ""
							}
						}
					},
					"patching_rect": [
						440.0,
						161.0,
						72.0,
						20.0
					],
					"saved_attribute_attributes": {
						"default_plcolor": {
							"expression": ""
						}
					},
					"text": "p PushBanks"
				}
			},
			{
				"box": {
					"angle": 270.0,
					"bgcolor": [
						0.113725490196078,
						0.113725490196078,
						0.113725490196078,
						1.0
					],
					"id": "obj-4",
					"maxclass": "panel",
					"mode": 0,
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						564.0,
						161.0,
						32.0,
						26.0
					],
					"presentation": 1,
					"presentation_rect": [
						4.0,
						4.0,
						268.0,
						111.0
					],
					"proportion": 0.39,
					"rounded": 4,
					"saved_attribute_attributes": {
						"bgfillcolor": {
							"expression": "themecolor.live_lcd_bg"
						}
					}
				}
			},
			{
				"box": {
					"id": "obj-30",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						283.0,
						408.0,
						50.0,
						20.0
					],
					"text": "clip~ 0 1"
				}
			},
			{
				"box": {
					"annotation": "The Fall amount smoothes the release of the envelope. ",
					"id": "obj-81",
					"maxclass": "live.dial",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"float"
					],
					"parameter_enable": 1,
					"patching_rect": [
						674.0,
						237.0,
						46.0,
						48.0
					],
					"presentation": 1,
					"presentation_rect": [
						118.0,
						118.0,
						45.0,
						48.0
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_linknames": 1,
							"parameter_longname": "Fall",
							"parameter_mapping_index": 3,
							"parameter_mmax": 100.0,
							"parameter_modmode": 2,
							"parameter_shortname": "Fall",
							"parameter_steps": 1,
							"parameter_type": 0,
							"parameter_unitstyle": 5
						}
					},
					"varname": "Fall"
				}
			},
			{
				"box": {
					"annotation": "The Rise amount smoothes the attack of the envelope. ",
					"id": "obj-77",
					"maxclass": "live.dial",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"float"
					],
					"parameter_enable": 1,
					"patching_rect": [
						579.0,
						237.0,
						46.0,
						48.0
					],
					"presentation": 1,
					"presentation_rect": [
						68.0,
						118.0,
						45.0,
						48.0
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_linknames": 1,
							"parameter_longname": "Rise",
							"parameter_mapping_index": 3,
							"parameter_mmax": 100.0,
							"parameter_modmode": 2,
							"parameter_shortname": "Rise",
							"parameter_steps": 1,
							"parameter_type": 0,
							"parameter_unitstyle": 5
						}
					},
					"varname": "Rise"
				}
			},
			{
				"box": {
					"annotation": "This sets the gain applied to the incoming signal.",
					"annotation_name": "Gain",
					"id": "obj-11",
					"maxclass": "live.dial",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"float"
					],
					"parameter_enable": 1,
					"patching_rect": [
						328.0,
						237.0,
						27.0,
						48.0
					],
					"presentation": 1,
					"presentation_rect": [
						18.0,
						118.0,
						45.0,
						48.0
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_annotation_name": "Gain",
							"parameter_exponent": 0.515,
							"parameter_initial": [
								0
							],
							"parameter_initial_enable": 1,
							"parameter_linknames": 1,
							"parameter_longname": "Gain",
							"parameter_mmax": 30.0,
							"parameter_mmin": -70.0,
							"parameter_modmode": 2,
							"parameter_shortname": "Gain",
							"parameter_type": 0,
							"parameter_unitstyle": 4
						}
					},
					"varname": "Gain"
				}
			},
			{
				"box": {
					"annotation": "The envelope of the signal will be delayed in sync.",
					"hidden": 1,
					"id": "obj-49",
					"maxclass": "live.dial",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"float"
					],
					"parameter_enable": 1,
					"patching_rect": [
						498.0,
						237.0,
						51.0,
						48.0
					],
					"presentation": 1,
					"presentation_rect": [
						168.0,
						118.0,
						45.0,
						48.0
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_enum": [
								"0",
								"1/32",
								"1/16",
								"1/8",
								"1/4",
								"1/2",
								"1"
							],
							"parameter_initial": [
								0
							],
							"parameter_initial_enable": 1,
							"parameter_linknames": 1,
							"parameter_longname": "Delay Synced",
							"parameter_mmax": 6,
							"parameter_modmode": 0,
							"parameter_shortname": "Delay",
							"parameter_steps": 6,
							"parameter_type": 2,
							"parameter_unitstyle": 9
						}
					},
					"varname": "Delay Synced"
				}
			},
			{
				"box": {
					"annotation": "Toggles the delay mode between beat synced and time-based (ms). ",
					"annotation_name": "Delay Mode",
					"id": "obj-38",
					"livemode": 1,
					"maxclass": "live.tab",
					"num_lines_patching": 1,
					"num_lines_presentation": 2,
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": [
						"",
						"",
						"float"
					],
					"parameter_enable": 1,
					"patching_rect": [
						375.0,
						161.0,
						45.0,
						19.0
					],
					"pictures": [
						"ms-icon.svg",
						"beat-icon.svg"
					],
					"presentation": 1,
					"presentation_rect": [
						220.0,
						140.0,
						21.0,
						26.0
					],
					"remapsvgcolors": 1,
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_annotation_name": "Delay Mode",
							"parameter_enum": [
								"Free",
								"Sync"
							],
							"parameter_linknames": 1,
							"parameter_longname": "Delay Mode",
							"parameter_mmax": 1,
							"parameter_modmode": 0,
							"parameter_order": 1,
							"parameter_shortname": "Delay Mode",
							"parameter_type": 2,
							"parameter_unitstyle": 9
						}
					},
					"usepicture": 1,
					"usesvgviewbox": 1,
					"varname": "Delay Mode"
				}
			},
			{
				"box": {
					"color": [
						1.0,
						0.694117647058824,
						0.0,
						1.0
					],
					"id": "obj-50",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"bang",
						"bang"
					],
					"patcher": {
						"fileversion": 1,
						"appversion": {
							"major": 9,
							"minor": 0,
							"revision": 8,
							"architecture": "x64",
							"modernui": 1
						},
						"classnamespace": "box",
						"rect": [
							431.0,
							545.0,
							345.0,
							269.0
						],
						"gridsize": [
							15.0,
							15.0
						],
						"boxes": [
							{
								"box": {
									"id": "obj-28",
									"maxclass": "newobj",
									"numinlets": 3,
									"numoutlets": 3,
									"outlettype": [
										"bang",
										"bang",
										""
									],
									"patching_rect": [
										30.0,
										116.0,
										95.0,
										22.0
									],
									"text": "sel 0 1"
								}
							},
							{
								"box": {
									"id": "obj-35",
									"maxclass": "newobj",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										"int"
									],
									"patching_rect": [
										244.0,
										82.0,
										33.0,
										22.0
									],
									"text": "== 0"
								}
							},
							{
								"box": {
									"comment": "to sync delay control",
									"id": "obj-4",
									"index": 2,
									"maxclass": "outlet",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										68.0,
										201.0,
										30.0,
										30.0
									]
								}
							},
							{
								"box": {
									"id": "obj-49",
									"maxclass": "message",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										244.0,
										116.0,
										61.0,
										22.0
									],
									"text": "hidden $1"
								}
							},
							{
								"box": {
									"comment": "to free control",
									"id": "obj-25",
									"index": 1,
									"maxclass": "outlet",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										30.0,
										201.0,
										30.0,
										30.0
									]
								}
							},
							{
								"box": {
									"id": "obj-24",
									"maxclass": "message",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										146.0,
										116.0,
										61.0,
										22.0
									],
									"text": "hidden $1"
								}
							},
							{
								"box": {
									"comment": "(bool) free / sync",
									"id": "obj-17",
									"index": 1,
									"maxclass": "inlet",
									"numinlets": 0,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										30.0,
										25.0,
										30.0,
										30.0
									]
								}
							}
						],
						"lines": [
							{
								"patchline": {
									"destination": [
										"obj-24",
										0
									],
									"order": 1,
									"source": [
										"obj-17",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-28",
										0
									],
									"order": 2,
									"source": [
										"obj-17",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-35",
										0
									],
									"order": 0,
									"source": [
										"obj-17",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-25",
										0
									],
									"source": [
										"obj-24",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-25",
										0
									],
									"source": [
										"obj-28",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-4",
										0
									],
									"source": [
										"obj-28",
										1
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-49",
										0
									],
									"source": [
										"obj-35",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-4",
										0
									],
									"source": [
										"obj-49",
										0
									]
								}
							}
						],
						"saved_attribute_attributes": {
							"default_plcolor": {
								"expression": ""
							}
						}
					},
					"patching_rect": [
						411.0,
						207.0,
						106.0,
						20.0
					],
					"saved_attribute_attributes": {
						"default_plcolor": {
							"expression": ""
						}
					},
					"text": "p Activate"
				}
			},
			{
				"box": {
					"color": [
						1.0,
						0.694117647058824,
						0.0,
						1.0
					],
					"id": "obj-48",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patcher": {
						"fileversion": 1,
						"appversion": {
							"major": 9,
							"minor": 0,
							"revision": 8,
							"architecture": "x64",
							"modernui": 1
						},
						"classnamespace": "box",
						"rect": [
							202.0,
							208.0,
							397.0,
							334.0
						],
						"gridsize": [
							15.0,
							15.0
						],
						"boxes": [
							{
								"box": {
									"id": "obj-3",
									"maxclass": "newobj",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										31.0,
										215.0,
										39.0,
										22.0
									],
									"text": "round"
								}
							},
							{
								"box": {
									"id": "obj-1",
									"maxclass": "message",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										31.0,
										107.0,
										30.0,
										22.0
									],
									"text": "0"
								}
							},
							{
								"box": {
									"id": "obj-93",
									"maxclass": "message",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										271.0,
										107.0,
										35.0,
										22.0
									],
									"text": "1920"
								}
							},
							{
								"box": {
									"id": "obj-92",
									"maxclass": "message",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										231.0,
										107.0,
										30.0,
										22.0
									],
									"text": "960"
								}
							},
							{
								"box": {
									"id": "obj-91",
									"maxclass": "message",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										191.0,
										107.0,
										30.0,
										22.0
									],
									"text": "480"
								}
							},
							{
								"box": {
									"id": "obj-90",
									"maxclass": "message",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										151.0,
										107.0,
										30.0,
										22.0
									],
									"text": "240"
								}
							},
							{
								"box": {
									"id": "obj-89",
									"maxclass": "message",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										111.0,
										107.0,
										30.0,
										22.0
									],
									"text": "120"
								}
							},
							{
								"box": {
									"id": "obj-87",
									"maxclass": "message",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										71.0,
										107.0,
										30.0,
										22.0
									],
									"text": "60"
								}
							},
							{
								"box": {
									"id": "obj-75",
									"maxclass": "newobj",
									"numinlets": 8,
									"numoutlets": 8,
									"outlettype": [
										"",
										"",
										"",
										"",
										"",
										"",
										"",
										""
									],
									"patching_rect": [
										31.0,
										68.0,
										299.0,
										22.0
									],
									"text": "route 0 1 2 3 4 5 6"
								}
							},
							{
								"box": {
									"id": "obj-49",
									"maxclass": "newobj",
									"numinlets": 1,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										31.0,
										176.0,
										130.0,
										22.0
									],
									"text": "translate ticks samples"
								}
							},
							{
								"box": {
									"comment": "(int, synced time periods)",
									"id": "obj-97",
									"index": 1,
									"maxclass": "inlet",
									"numinlets": 0,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										31.0,
										21.0,
										30.0,
										30.0
									]
								}
							},
							{
								"box": {
									"comment": "(int) samples",
									"id": "obj-99",
									"index": 1,
									"maxclass": "outlet",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										31.0,
										254.0,
										30.0,
										30.0
									]
								}
							}
						],
						"lines": [
							{
								"patchline": {
									"destination": [
										"obj-49",
										0
									],
									"source": [
										"obj-1",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-99",
										0
									],
									"source": [
										"obj-3",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-3",
										0
									],
									"source": [
										"obj-49",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-1",
										0
									],
									"source": [
										"obj-75",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-87",
										0
									],
									"source": [
										"obj-75",
										1
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-89",
										0
									],
									"source": [
										"obj-75",
										2
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-90",
										0
									],
									"source": [
										"obj-75",
										3
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-91",
										0
									],
									"source": [
										"obj-75",
										4
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-92",
										0
									],
									"source": [
										"obj-75",
										5
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-93",
										0
									],
									"source": [
										"obj-75",
										6
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-49",
										0
									],
									"source": [
										"obj-87",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-49",
										0
									],
									"source": [
										"obj-89",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-49",
										0
									],
									"source": [
										"obj-90",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-49",
										0
									],
									"source": [
										"obj-91",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-49",
										0
									],
									"source": [
										"obj-92",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-49",
										0
									],
									"source": [
										"obj-93",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-75",
										0
									],
									"source": [
										"obj-97",
										0
									]
								}
							}
						],
						"saved_attribute_attributes": {
							"default_plcolor": {
								"expression": ""
							}
						}
					},
					"patching_rect": [
						498.0,
						295.0,
						79.0,
						20.0
					],
					"saved_attribute_attributes": {
						"default_plcolor": {
							"expression": ""
						}
					},
					"text": "p ConvertSync"
				}
			},
			{
				"box": {
					"color": [
						1.0,
						0.694117647058824,
						0.0,
						1.0
					],
					"id": "obj-28",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patcher": {
						"fileversion": 1,
						"appversion": {
							"major": 9,
							"minor": 0,
							"revision": 8,
							"architecture": "x64",
							"modernui": 1
						},
						"classnamespace": "box",
						"rect": [
							196.0,
							187.0,
							227.0,
							227.0
						],
						"gridsize": [
							15.0,
							15.0
						],
						"boxes": [
							{
								"box": {
									"id": "obj-10",
									"maxclass": "newobj",
									"numinlets": 1,
									"numoutlets": 2,
									"outlettype": [
										"signal",
										"float"
									],
									"patching_rect": [
										32.0,
										63.0,
										77.0,
										22.0
									],
									"text": "mstosamps~"
								}
							},
							{
								"box": {
									"id": "obj-1",
									"maxclass": "newobj",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										90.0,
										102.0,
										39.0,
										22.0
									],
									"text": "round"
								}
							},
							{
								"box": {
									"comment": "(float, ms) time",
									"id": "obj-65",
									"index": 1,
									"maxclass": "inlet",
									"numinlets": 0,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										32.0,
										16.0,
										30.0,
										30.0
									]
								}
							},
							{
								"box": {
									"comment": "(int) samples",
									"id": "obj-66",
									"index": 1,
									"maxclass": "outlet",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										90.0,
										141.0,
										30.0,
										30.0
									]
								}
							}
						],
						"lines": [
							{
								"patchline": {
									"destination": [
										"obj-66",
										0
									],
									"source": [
										"obj-1",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-1",
										0
									],
									"source": [
										"obj-10",
										1
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-10",
										0
									],
									"source": [
										"obj-65",
										0
									]
								}
							}
						],
						"saved_attribute_attributes": {
							"default_plcolor": {
								"expression": ""
							}
						}
					},
					"patching_rect": [
						411.0,
						295.0,
						76.0,
						20.0
					],
					"saved_attribute_attributes": {
						"default_plcolor": {
							"expression": ""
						}
					},
					"text": "p ConvertFree"
				}
			},
			{
				"box": {
					"color": [
						1.0,
						0.694117647058824,
						0.0,
						1.0
					],
					"id": "obj-85",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patcher": {
						"fileversion": 1,
						"appversion": {
							"major": 9,
							"minor": 0,
							"revision": 8,
							"architecture": "x64",
							"modernui": 1
						},
						"classnamespace": "box",
						"rect": [
							170.0,
							195.0,
							423.0,
							347.0
						],
						"gridsize": [
							15.0,
							15.0
						],
						"boxes": [
							{
								"box": {
									"id": "obj-6",
									"maxclass": "newobj",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										"float"
									],
									"patching_rect": [
										32.0,
										70.0,
										33.0,
										22.0
									],
									"text": "* 0.5"
								}
							},
							{
								"box": {
									"id": "obj-3",
									"maxclass": "newobj",
									"numinlets": 1,
									"numoutlets": 2,
									"outlettype": [
										"bang",
										"float"
									],
									"patching_rect": [
										97.0,
										70.0,
										30.0,
										22.0
									],
									"text": "t b f"
								}
							},
							{
								"box": {
									"id": "obj-63",
									"maxclass": "newobj",
									"numinlets": 1,
									"numoutlets": 4,
									"outlettype": [
										"int",
										"float",
										"int",
										"int"
									],
									"patching_rect": [
										81.0,
										31.0,
										67.0,
										22.0
									],
									"text": "dspstate~"
								}
							},
							{
								"box": {
									"id": "obj-5",
									"maxclass": "newobj",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										"float"
									],
									"patching_rect": [
										32.0,
										139.0,
										95.0,
										22.0
									],
									"text": "* 0."
								}
							},
							{
								"box": {
									"id": "obj-1",
									"maxclass": "newobj",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										32.0,
										178.0,
										39.0,
										22.0
									],
									"text": "round"
								}
							},
							{
								"box": {
									"bubble": 1,
									"bubbleusescolors": 1,
									"id": "obj-2",
									"linecount": 3,
									"maxclass": "comment",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										167.0,
										41.0,
										216.0,
										51.0
									],
									"saved_attribute_attributes": {
										"textcolor": {
											"expression": "themecolor.live_control_fg"
										}
									},
									"text": "Convert value 0-1 to samples (according to current sample rate), with rounding to nearest integer."
								}
							},
							{
								"box": {
									"comment": "(float, 0 - 1) time",
									"id": "obj-65",
									"index": 1,
									"maxclass": "inlet",
									"numinlets": 0,
									"numoutlets": 1,
									"outlettype": [
										"float"
									],
									"patching_rect": [
										32.0,
										31.0,
										30.0,
										30.0
									]
								}
							},
							{
								"box": {
									"comment": "(int) ramp time in samples",
									"id": "obj-66",
									"index": 1,
									"maxclass": "outlet",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										32.0,
										217.0,
										30.0,
										30.0
									]
								}
							}
						],
						"lines": [
							{
								"patchline": {
									"destination": [
										"obj-66",
										0
									],
									"source": [
										"obj-1",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-5",
										1
									],
									"source": [
										"obj-3",
										1
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-5",
										0
									],
									"source": [
										"obj-3",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-1",
										0
									],
									"source": [
										"obj-5",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-5",
										0
									],
									"source": [
										"obj-6",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-3",
										0
									],
									"source": [
										"obj-63",
										1
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-6",
										0
									],
									"source": [
										"obj-65",
										0
									]
								}
							}
						],
						"saved_attribute_attributes": {
							"default_plcolor": {
								"expression": ""
							}
						}
					},
					"patching_rect": [
						701.0,
						295.0,
						83.0,
						20.0
					],
					"saved_attribute_attributes": {
						"default_plcolor": {
							"expression": ""
						}
					},
					"text": "p ConvertRamp"
				}
			},
			{
				"box": {
					"id": "obj-54",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						46.0,
						340.0,
						65.0,
						20.0
					],
					"text": "*~ 0.707107"
				}
			},
			{
				"box": {
					"color": [
						1.0,
						0.694117647058824,
						0.0,
						1.0
					],
					"id": "obj-113",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patcher": {
						"fileversion": 1,
						"appversion": {
							"major": 9,
							"minor": 0,
							"revision": 8,
							"architecture": "x64",
							"modernui": 1
						},
						"classnamespace": "box",
						"rect": [
							170.0,
							195.0,
							423.0,
							347.0
						],
						"gridsize": [
							15.0,
							15.0
						],
						"boxes": [
							{
								"box": {
									"id": "obj-6",
									"maxclass": "newobj",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										"float"
									],
									"patching_rect": [
										32.0,
										70.0,
										33.0,
										22.0
									],
									"text": "* 0.5"
								}
							},
							{
								"box": {
									"id": "obj-3",
									"maxclass": "newobj",
									"numinlets": 1,
									"numoutlets": 2,
									"outlettype": [
										"bang",
										"float"
									],
									"patching_rect": [
										97.0,
										70.0,
										30.0,
										22.0
									],
									"text": "t b f"
								}
							},
							{
								"box": {
									"id": "obj-63",
									"maxclass": "newobj",
									"numinlets": 1,
									"numoutlets": 4,
									"outlettype": [
										"int",
										"float",
										"int",
										"int"
									],
									"patching_rect": [
										81.0,
										31.0,
										67.0,
										22.0
									],
									"text": "dspstate~"
								}
							},
							{
								"box": {
									"id": "obj-5",
									"maxclass": "newobj",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										"float"
									],
									"patching_rect": [
										32.0,
										139.0,
										95.0,
										22.0
									],
									"text": "* 0."
								}
							},
							{
								"box": {
									"id": "obj-1",
									"maxclass": "newobj",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										32.0,
										178.0,
										39.0,
										22.0
									],
									"text": "round"
								}
							},
							{
								"box": {
									"bubble": 1,
									"bubbleusescolors": 1,
									"id": "obj-2",
									"linecount": 3,
									"maxclass": "comment",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										167.0,
										41.0,
										216.0,
										51.0
									],
									"saved_attribute_attributes": {
										"textcolor": {
											"expression": "themecolor.live_control_fg"
										}
									},
									"text": "Convert value 0-1 to samples (according to current sample rate), with rounding to nearest integer."
								}
							},
							{
								"box": {
									"comment": "(float, 0 - 1) time",
									"id": "obj-65",
									"index": 1,
									"maxclass": "inlet",
									"numinlets": 0,
									"numoutlets": 1,
									"outlettype": [
										"float"
									],
									"patching_rect": [
										32.0,
										31.0,
										30.0,
										30.0
									]
								}
							},
							{
								"box": {
									"comment": "(int) ramp time in samples",
									"id": "obj-66",
									"index": 1,
									"maxclass": "outlet",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										32.0,
										217.0,
										30.0,
										30.0
									]
								}
							}
						],
						"lines": [
							{
								"patchline": {
									"destination": [
										"obj-66",
										0
									],
									"source": [
										"obj-1",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-5",
										1
									],
									"source": [
										"obj-3",
										1
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-5",
										0
									],
									"source": [
										"obj-3",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-1",
										0
									],
									"source": [
										"obj-5",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-5",
										0
									],
									"source": [
										"obj-6",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-3",
										0
									],
									"source": [
										"obj-63",
										1
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-6",
										0
									],
									"source": [
										"obj-65",
										0
									]
								}
							}
						],
						"saved_attribute_attributes": {
							"default_plcolor": {
								"expression": ""
							}
						}
					},
					"patching_rect": [
						606.0,
						295.0,
						83.0,
						20.0
					],
					"saved_attribute_attributes": {
						"default_plcolor": {
							"expression": ""
						}
					},
					"text": "p ConvertRamp"
				}
			},
			{
				"box": {
					"color": [
						1.0,
						0.694117647058824,
						0.0,
						1.0
					],
					"id": "obj-59",
					"maxclass": "newobj",
					"numinlets": 5,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patcher": {
						"fileversion": 1,
						"appversion": {
							"major": 9,
							"minor": 0,
							"revision": 8,
							"architecture": "x64",
							"modernui": 1
						},
						"classnamespace": "box",
						"rect": [
							236.0,
							168.0,
							658.0,
							340.0
						],
						"gridsize": [
							15.0,
							15.0
						],
						"boxes": [
							{
								"box": {
									"id": "obj-2",
									"maxclass": "newobj",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										"signal"
									],
									"patching_rect": [
										332.0,
										140.0,
										115.0,
										22.0
									],
									"text": "delay~ 1058400"
								}
							},
							{
								"box": {
									"comment": "(int, samples) offset",
									"id": "obj-8",
									"index": 3,
									"maxclass": "inlet",
									"numinlets": 0,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										428.0,
										23.0,
										30.0,
										30.0
									]
								}
							},
							{
								"box": {
									"comment": "(int, samples) fall",
									"id": "obj-7",
									"index": 5,
									"maxclass": "inlet",
									"numinlets": 0,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										596.0,
										23.0,
										30.0,
										30.0
									]
								}
							},
							{
								"box": {
									"comment": "(int, samples) rise",
									"id": "obj-6",
									"index": 4,
									"maxclass": "inlet",
									"numinlets": 0,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										464.0,
										23.0,
										30.0,
										30.0
									]
								}
							},
							{
								"box": {
									"comment": "(float, dB) gain",
									"id": "obj-5",
									"index": 2,
									"maxclass": "inlet",
									"numinlets": 0,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										388.0,
										23.0,
										30.0,
										30.0
									]
								}
							},
							{
								"box": {
									"bubble": 1,
									"bubbleside": 3,
									"bubbleusescolors": 1,
									"id": "obj-23",
									"linecount": 2,
									"maxclass": "comment",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										200.0,
										210.5,
										120.0,
										37.0
									],
									"saved_attribute_attributes": {
										"textcolor": {
											"expression": "themecolor.live_control_fg"
										}
									},
									"text": "Logarithmic filter:\nAttack, Release"
								}
							},
							{
								"box": {
									"id": "obj-4",
									"maxclass": "newobj",
									"numinlets": 3,
									"numoutlets": 1,
									"outlettype": [
										"signal"
									],
									"patching_rect": [
										332.0,
										218.0,
										283.0,
										22.0
									],
									"text": "slide~"
								}
							},
							{
								"box": {
									"color": [
										1.0,
										0.694117647058824,
										0.0,
										1.0
									],
									"id": "obj-74",
									"maxclass": "newobj",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										"signal"
									],
									"patcher": {
										"fileversion": 1,
										"appversion": {
											"major": 9,
											"minor": 0,
											"revision": 8,
											"architecture": "x64",
											"modernui": 1
										},
										"classnamespace": "box",
										"rect": [
											303.0,
											214.0,
											360.0,
											391.0
										],
										"gridsize": [
											15.0,
											15.0
										],
										"boxes": [
											{
												"box": {
													"id": "obj-23",
													"maxclass": "newobj",
													"numinlets": 1,
													"numoutlets": 3,
													"outlettype": [
														"bang",
														"int",
														"int"
													],
													"patching_rect": [
														70.0,
														72.0,
														83.0,
														22.0
													],
													"text": "live.thisdevice"
												}
											},
											{
												"box": {
													"bubble": 1,
													"bubbleusescolors": 1,
													"id": "obj-17",
													"maxclass": "comment",
													"numinlets": 1,
													"numoutlets": 0,
													"patching_rect": [
														155.0,
														149.0,
														146.0,
														24.0
													],
													"saved_attribute_attributes": {
														"textcolor": {
															"expression": "themecolor.live_control_fg"
														}
													},
													"text": "Multiply active by gain."
												}
											},
											{
												"box": {
													"id": "obj-16",
													"maxclass": "newobj",
													"numinlets": 2,
													"numoutlets": 1,
													"outlettype": [
														"float"
													],
													"patching_rect": [
														102.0,
														149.0,
														33.0,
														22.0
													],
													"text": "* 1."
												}
											},
											{
												"box": {
													"id": "obj-15",
													"maxclass": "newobj",
													"numinlets": 2,
													"numoutlets": 1,
													"outlettype": [
														""
													],
													"patching_rect": [
														102.0,
														111.0,
														101.0,
														22.0
													],
													"text": "pak 1. 1."
												}
											},
											{
												"box": {
													"bubble": 1,
													"bubbleusescolors": 1,
													"id": "obj-14",
													"maxclass": "comment",
													"numinlets": 1,
													"numoutlets": 0,
													"patching_rect": [
														155.0,
														187.0,
														155.0,
														24.0
													],
													"saved_attribute_attributes": {
														"textcolor": {
															"expression": "themecolor.live_control_fg"
														}
													},
													"text": "Ramp to value in 50 ms."
												}
											},
											{
												"box": {
													"id": "obj-13",
													"maxclass": "message",
													"numinlets": 2,
													"numoutlets": 1,
													"outlettype": [
														""
													],
													"patching_rect": [
														102.0,
														187.0,
														39.0,
														22.0
													],
													"text": "$1 50"
												}
											},
											{
												"box": {
													"id": "obj-3",
													"maxclass": "newobj",
													"numinlets": 2,
													"numoutlets": 2,
													"outlettype": [
														"signal",
														"bang"
													],
													"patching_rect": [
														102.0,
														225.0,
														48.0,
														22.0
													],
													"text": "line~ 1."
												}
											},
											{
												"box": {
													"comment": "(float, dB) gain",
													"id": "obj-2",
													"index": 2,
													"maxclass": "inlet",
													"numinlets": 0,
													"numoutlets": 1,
													"outlettype": [
														""
													],
													"patching_rect": [
														184.0,
														25.0,
														30.0,
														30.0
													]
												}
											},
											{
												"box": {
													"id": "obj-49",
													"maxclass": "newobj",
													"numinlets": 1,
													"numoutlets": 1,
													"outlettype": [
														""
													],
													"patching_rect": [
														184.0,
														72.0,
														39.0,
														22.0
													],
													"text": "dbtoa"
												}
											},
											{
												"box": {
													"id": "obj-25",
													"maxclass": "newobj",
													"numinlets": 2,
													"numoutlets": 1,
													"outlettype": [
														"signal"
													],
													"patching_rect": [
														26.0,
														264.0,
														95.0,
														22.0
													],
													"text": "*~ 1."
												}
											},
											{
												"box": {
													"comment": "(signal) input",
													"id": "obj-65",
													"index": 1,
													"maxclass": "inlet",
													"numinlets": 0,
													"numoutlets": 1,
													"outlettype": [
														"signal"
													],
													"patching_rect": [
														26.0,
														27.0,
														30.0,
														30.0
													]
												}
											},
											{
												"box": {
													"comment": "(signal) scaled",
													"id": "obj-66",
													"index": 1,
													"maxclass": "outlet",
													"numinlets": 1,
													"numoutlets": 0,
													"patching_rect": [
														26.0,
														304.0,
														30.0,
														30.0
													]
												}
											}
										],
										"lines": [
											{
												"patchline": {
													"destination": [
														"obj-3",
														0
													],
													"source": [
														"obj-13",
														0
													]
												}
											},
											{
												"patchline": {
													"destination": [
														"obj-16",
														0
													],
													"source": [
														"obj-15",
														0
													]
												}
											},
											{
												"patchline": {
													"destination": [
														"obj-13",
														0
													],
													"source": [
														"obj-16",
														0
													]
												}
											},
											{
												"patchline": {
													"destination": [
														"obj-49",
														0
													],
													"source": [
														"obj-2",
														0
													]
												}
											},
											{
												"patchline": {
													"destination": [
														"obj-15",
														0
													],
													"source": [
														"obj-23",
														1
													]
												}
											},
											{
												"patchline": {
													"destination": [
														"obj-66",
														0
													],
													"source": [
														"obj-25",
														0
													]
												}
											},
											{
												"patchline": {
													"destination": [
														"obj-25",
														1
													],
													"source": [
														"obj-3",
														0
													]
												}
											},
											{
												"patchline": {
													"destination": [
														"obj-15",
														1
													],
													"source": [
														"obj-49",
														0
													]
												}
											},
											{
												"patchline": {
													"destination": [
														"obj-25",
														0
													],
													"source": [
														"obj-65",
														0
													]
												}
											}
										],
										"saved_attribute_attributes": {
											"default_plcolor": {
												"expression": ""
											}
										}
									},
									"patching_rect": [
										332.0,
										71.0,
										75.0,
										22.0
									],
									"saved_attribute_attributes": {
										"default_plcolor": {
											"expression": ""
										}
									},
									"text": "p ActiveAmp"
								}
							},
							{
								"box": {
									"id": "obj-3",
									"maxclass": "newobj",
									"numinlets": 1,
									"numoutlets": 1,
									"outlettype": [
										"signal"
									],
									"patching_rect": [
										332.0,
										179.0,
										112.0,
										22.0
									],
									"text": "average~ 1000 rms"
								}
							},
							{
								"box": {
									"comment": "(signal) audio in",
									"id": "obj-38",
									"index": 1,
									"maxclass": "inlet",
									"numinlets": 0,
									"numoutlets": 1,
									"outlettype": [
										"signal"
									],
									"patching_rect": [
										332.0,
										23.0,
										30.0,
										30.0
									]
								}
							},
							{
								"box": {
									"comment": "(signal) envelope",
									"id": "obj-41",
									"index": 1,
									"maxclass": "outlet",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										332.0,
										257.0,
										30.0,
										30.0
									]
								}
							},
							{
								"box": {
									"bubble": 1,
									"bubbleside": 3,
									"bubbleusescolors": 1,
									"id": "obj-1",
									"linecount": 4,
									"maxclass": "comment",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										24.0,
										80.0,
										185.0,
										64.0
									],
									"saved_attribute_attributes": {
										"textcolor": {
											"expression": "themecolor.live_control_fg"
										}
									},
									"text": "Allocate delay memory:\n12 = 4 (4n notes) * 3 sec (1n note at 60BPM take 1 sec, at 20 BPM take 3 secs)"
								}
							},
							{
								"box": {
									"id": "obj-9",
									"maxclass": "newobj",
									"numinlets": 1,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										216.0,
										140.0,
										100.0,
										22.0
									],
									"text": "prepend maxsize"
								}
							},
							{
								"box": {
									"id": "obj-19",
									"maxclass": "newobj",
									"numinlets": 2,
									"numoutlets": 1,
									"outlettype": [
										"int"
									],
									"patching_rect": [
										216.0,
										101.0,
										33.0,
										22.0
									],
									"text": "* 12"
								}
							},
							{
								"box": {
									"id": "obj-13",
									"maxclass": "newobj",
									"numinlets": 1,
									"numoutlets": 4,
									"outlettype": [
										"int",
										"float",
										"int",
										"int"
									],
									"patching_rect": [
										200.0,
										62.0,
										68.0,
										22.0
									],
									"text": "dspstate~"
								}
							}
						],
						"lines": [
							{
								"patchline": {
									"destination": [
										"obj-19",
										0
									],
									"source": [
										"obj-13",
										1
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-9",
										0
									],
									"source": [
										"obj-19",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-3",
										0
									],
									"source": [
										"obj-2",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-4",
										0
									],
									"source": [
										"obj-3",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-74",
										0
									],
									"source": [
										"obj-38",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-41",
										0
									],
									"source": [
										"obj-4",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-74",
										1
									],
									"source": [
										"obj-5",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-4",
										1
									],
									"source": [
										"obj-6",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-4",
										2
									],
									"source": [
										"obj-7",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-2",
										0
									],
									"source": [
										"obj-74",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-2",
										1
									],
									"source": [
										"obj-8",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-2",
										0
									],
									"source": [
										"obj-9",
										0
									]
								}
							}
						],
						"saved_attribute_attributes": {
							"default_plcolor": {
								"expression": ""
							}
						}
					},
					"patching_rect": [
						283.0,
						378.0,
						200.0,
						20.0
					],
					"saved_attribute_attributes": {
						"default_plcolor": {
							"expression": ""
						}
					},
					"text": "p envelopeFolower"
				}
			},
			{
				"box": {
					"id": "obj-2",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 2,
					"outlettype": [
						"signal",
						"signal"
					],
					"patching_rect": [
						46.0,
						621.0,
						51.0,
						20.0
					],
					"text": "plugout~"
				}
			},
			{
				"box": {
					"id": "obj-9",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 2,
					"outlettype": [
						"signal",
						"signal"
					],
					"patching_rect": [
						46.0,
						591.0,
						51.0,
						20.0
					],
					"text": "plugin~"
				}
			},
			{
				"box": {
					"fontname": "Ableton Sans Medium",
					"fontsize": 11.0,
					"id": "obj-34",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						162.0,
						16.0,
						218.0,
						20.0
					],
					"prototypename": "M4L.patcher-summary",
					"saved_attribute_attributes": {
						"textcolor": {
							"expression": "themecolor.live_control_fg"
						}
					},
					"text": "Envelope following with OSC export for external control systems."
				}
			},
			{
				"box": {
					"fontname": "Ableton Sans Medium",
					"fontsize": 18.0,
					"id": "obj-33",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						8.0,
						8.0,
						152.0,
						28.0
					],
					"prototypename": "M4L.subpatcher-title",
					"saved_attribute_attributes": {
						"textcolor": {
							"expression": "themecolor.live_control_fg"
						}
					},
					"text": "Envelope Follower OSC Bridge"
				}
			},
			{
				"box": {
					"fontname": "Ableton Sans Medium",
					"fontsize": 11.0,
					"id": "obj-29",
					"linecount": 3,
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						8.0,
						38.0,
						563.0,
						46.0
					],
					"prototypename": "M4L.patcher-story",
					"saved_attribute_attributes": {
						"textcolor": {
							"expression": "themecolor.live_control_fg"
						}
					},
					"text": "Envelope following is a well-known technique which consists in capturing a signal, smoothing and reshaping its amplitude course in order to obtain a more or less continuous curve, and finally mapping the curve to one or more control parameters. The \"autowah\" effect is perhaps the most well-known popular application of that technique. "
				}
			},
			{
				"box": {
					"annotation": "The envelope of the signal will be delayed ",
					"id": "obj-19",
					"maxclass": "live.dial",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"float"
					],
					"parameter_enable": 1,
					"patching_rect": [
						411.0,
						237.0,
						46.0,
						48.0
					],
					"presentation": 1,
					"presentation_rect": [
						168.0,
						118.0,
						45.0,
						48.0
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "Delay",
							"parameter_mapping_index": 2,
							"parameter_mmax": 500.0,
							"parameter_modmode": 2,
							"parameter_shortname": "Delay",
							"parameter_steps": 1,
							"parameter_type": 0,
							"parameter_units": "Smp",
							"parameter_unitstyle": 2
						}
					},
					"varname": "Delay"
				}
			},
			{
				"box": {
					"id": "obj-sb-snapshot",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						500.0,
						500.0,
						81.0,
						22.0
					],
					"text": "snapshot~ 16"
				}
			},
			{
				"box": {
					"id": "obj-sb-gate-expr",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						500.0,
						540.0,
						145.0,
						22.0
					],
					"text": "expr $f1 * ($f1 >= $f2)"
				}
			},
			{
				"box": {
					"id": "obj-sb-invert-expr",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						500.0,
						580.0,
						153.0,
						22.0
					],
					"text": "expr $f1 + $i2 * (1. - 2.*$f1)"
				}
			},
			{
				"box": {
					"id": "obj-sb-clip",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						500.0,
						620.0,
						73.0,
						22.0
					],
					"text": "clip 0. 1."
				}
			},
			{
				"box": {
					"id": "obj-sb-active-gate",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						500.0,
						660.0,
						60.0,
						22.0
					],
					"text": "gate 1 1"
				}
			},
			{
				"box": {
					"id": "obj-sb-prepend",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						500.0,
						700.0,
						146.0,
						22.0
					],
					"text": "prepend /Params/Param1"
				}
			},
			{
				"box": {
					"id": "obj-sb-udpsend",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						500.0,
						740.0,
						155.0,
						22.0
					],
					"text": "udpsend 127.0.0.1 3333"
				}
			},
			{
				"box": {
					"id": "obj-sb-sprintf",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						750.0,
						620.0,
						150.0,
						22.0
					],
					"text": "sprintf set /Params/%s"
				}
			},
			{
				"box": {
					"id": "obj-sb-port-msg",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						750.0,
						700.0,
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
					"patching_rect": [
						750.0,
						500.0,
						100.0,
						15.0
					],
					"presentation": 1,
					"presentation_rect": [
						18.0,
						175.0,
						110.0,
						15.0
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_enum": [
								"Param1",
								"Param2",
								"Param3",
								"Param4",
								"Param5",
								"Param6",
								"Param7",
								"Param8"
							],
							"parameter_initial": [
								0
							],
							"parameter_initial_enable": 1,
							"parameter_longname": "Param Name",
							"parameter_mmax": 7,
							"parameter_modmode": 0,
							"parameter_shortname": "Param",
							"parameter_type": 2
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
					"patching_rect": [
						700.0,
						660.0,
						24.0,
						24.0
					],
					"presentation": 1,
					"presentation_rect": [
						118.0,
						217.0,
						20.0,
						20.0
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_enum": [
								"off",
								"on"
							],
							"parameter_initial": [
								1
							],
							"parameter_initial_enable": 1,
							"parameter_longname": "Active",
							"parameter_mmax": 1,
							"parameter_modmode": 0,
							"parameter_shortname": "Active",
							"parameter_type": 2
						}
					},
					"varname": "Active"
				}
			},
			{
				"box": {
					"id": "obj-sb-gate-dial",
					"maxclass": "live.dial",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"float"
					],
					"parameter_enable": 1,
					"patching_rect": [
						670.0,
						540.0,
						44.0,
						48.0
					],
					"presentation": 1,
					"presentation_rect": [
						18.0,
						195.0,
						44.0,
						48.0
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_initial": [
								0.0
							],
							"parameter_initial_enable": 1,
							"parameter_longname": "Gate",
							"parameter_mmax": 1.0,
							"parameter_modmode": 0,
							"parameter_shortname": "Gate",
							"parameter_type": 0,
							"parameter_unitstyle": 1
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
					"patching_rect": [
						670.0,
						580.0,
						24.0,
						24.0
					],
					"presentation": 1,
					"presentation_rect": [
						78.0,
						217.0,
						20.0,
						20.0
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_enum": [
								"off",
								"on"
							],
							"parameter_initial": [
								0
							],
							"parameter_initial_enable": 1,
							"parameter_longname": "Invert",
							"parameter_mmax": 1,
							"parameter_modmode": 0,
							"parameter_shortname": "Inv",
							"parameter_type": 2
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
					"patching_rect": [
						750.0,
						660.0,
						56.0,
						15.0
					],
					"presentation": 1,
					"presentation_rect": [
						155.0,
						217.0,
						56.0,
						15.0
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_initial": [
								3333.0
							],
							"parameter_initial_enable": 1,
							"parameter_longname": "Dest Port",
							"parameter_mmax": 65535.0,
							"parameter_mmin": 1.0,
							"parameter_modmode": 0,
							"parameter_shortname": "Port",
							"parameter_steps": 65535,
							"parameter_type": 0,
							"parameter_unitstyle": 0
						}
					},
					"varname": "DestPort"
				}
			},
			{
				"box": {
					"fontsize": 9.0,
					"id": "obj-sb-inv-label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						700.0,
						582.0,
						30.0,
						17.0
					],
					"presentation": 1,
					"presentation_rect": [
						75.0,
						199.0,
						25.0,
						17.0
					],
					"text": "Inv"
				}
			},
			{
				"box": {
					"fontsize": 9.0,
					"id": "obj-sb-port-label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						810.0,
						662.0,
						30.0,
						17.0
					],
					"presentation": 1,
					"presentation_rect": [
						160.0,
						199.0,
						30.0,
						17.0
					],
					"text": "Port"
				}
			},
			{
				"box": {
					"fontsize": 9.0,
					"id": "obj-sb-osc-label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						750.0,
						480.0,
						80.0,
						17.0
					],
					"presentation": 1,
					"presentation_rect": [
						135.0,
						175.0,
						80.0,
						17.0
					],
					"text": "OSC Output",
					"textcolor": [
						0.93,
						0.69,
						0.2,
						1.0
					]
				}
			},
			{
				"box": {
					"fontsize": 9.0,
					"id": "obj-sb-active-label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						700.0,
						690.0,
						40.0,
						17.0
					],
					"presentation": 1,
					"presentation_rect": [
						115.0,
						199.0,
						25.0,
						17.0
					],
					"text": "On"
				}
			},
			{
				"box": {
					"id": "obj-sb-divider",
					"maxclass": "live.line",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						740.0,
						460.0,
						5.0,
						100.0
					]
				}
			},
			{
				"box": {
					"id": "obj-sb-sep-line",
					"maxclass": "live.line",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						700.0,
						450.0,
						200.0,
						5.0
					],
					"presentation": 1,
					"presentation_rect": [
						18.0,
						170.0,
						253.0,
						5.0
					],
					"linecolor": [
						0.3,
						0.3,
						0.3,
						1.0
					]
				}
			}
		],
		"lines": [
			{
				"patchline": {
					"destination": [
						"obj-3",
						2
					],
					"source": [
						"obj-1",
						2
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-3",
						1
					],
					"source": [
						"obj-1",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-3",
						0
					],
					"source": [
						"obj-1",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-1",
						8
					],
					"order": 0,
					"source": [
						"obj-10",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-27",
						1
					],
					"order": 1,
					"source": [
						"obj-10",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-59",
						1
					],
					"source": [
						"obj-11",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-59",
						3
					],
					"source": [
						"obj-113",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-37",
						0
					],
					"source": [
						"obj-14",
						2
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-54",
						0
					],
					"source": [
						"obj-14",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-54",
						0
					],
					"source": [
						"obj-14",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-14",
						3
					],
					"source": [
						"obj-16",
						3
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-14",
						2
					],
					"source": [
						"obj-16",
						2
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-14",
						1
					],
					"source": [
						"obj-16",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-14",
						0
					],
					"source": [
						"obj-16",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-28",
						0
					],
					"source": [
						"obj-19",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-20",
						0
					],
					"order": 1,
					"source": [
						"obj-21",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-8",
						0
					],
					"order": 0,
					"source": [
						"obj-21",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-55",
						0
					],
					"source": [
						"obj-25",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-13",
						0
					],
					"source": [
						"obj-27",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-6",
						1
					],
					"source": [
						"obj-28",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-1",
						7
					],
					"source": [
						"obj-3",
						6
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-1",
						6
					],
					"source": [
						"obj-3",
						5
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-1",
						5
					],
					"source": [
						"obj-3",
						4
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-1",
						4
					],
					"source": [
						"obj-3",
						3
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-1",
						3
					],
					"source": [
						"obj-3",
						2
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-1",
						2
					],
					"source": [
						"obj-3",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-1",
						1
					],
					"source": [
						"obj-3",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-7",
						0
					],
					"order": 0,
					"source": [
						"obj-30",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-8",
						0
					],
					"order": 1,
					"source": [
						"obj-30",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-25",
						0
					],
					"source": [
						"obj-37",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-40",
						0
					],
					"order": 2,
					"source": [
						"obj-38",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-5",
						0
					],
					"order": 0,
					"source": [
						"obj-38",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-50",
						0
					],
					"order": 1,
					"source": [
						"obj-38",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-6",
						0
					],
					"source": [
						"obj-40",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-6",
						2
					],
					"source": [
						"obj-48",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-48",
						0
					],
					"source": [
						"obj-49",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-19",
						0
					],
					"source": [
						"obj-50",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-49",
						0
					],
					"source": [
						"obj-50",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-20",
						0
					],
					"order": 1,
					"source": [
						"obj-54",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-59",
						0
					],
					"order": 0,
					"source": [
						"obj-54",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-12",
						0
					],
					"source": [
						"obj-55",
						2
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-22",
						0
					],
					"source": [
						"obj-55",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-31",
						0
					],
					"source": [
						"obj-55",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-30",
						0
					],
					"source": [
						"obj-59",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-59",
						2
					],
					"source": [
						"obj-6",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-1",
						0
					],
					"order": 0,
					"source": [
						"obj-7",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-27",
						0
					],
					"order": 1,
					"source": [
						"obj-7",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-113",
						0
					],
					"source": [
						"obj-77",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-85",
						0
					],
					"source": [
						"obj-81",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-59",
						4
					],
					"source": [
						"obj-85",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-2",
						1
					],
					"source": [
						"obj-9",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-2",
						0
					],
					"source": [
						"obj-9",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-sb-snapshot",
						0
					],
					"source": [
						"obj-30",
						0
					],
					"order": 2
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-sb-gate-expr",
						0
					],
					"source": [
						"obj-sb-snapshot",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-sb-gate-expr",
						1
					],
					"source": [
						"obj-sb-gate-dial",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-sb-invert-expr",
						0
					],
					"source": [
						"obj-sb-gate-expr",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-sb-invert-expr",
						1
					],
					"source": [
						"obj-invert",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-sb-clip",
						0
					],
					"source": [
						"obj-sb-invert-expr",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-sb-active-gate",
						1
					],
					"source": [
						"obj-sb-clip",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-sb-active-gate",
						0
					],
					"source": [
						"obj-active",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-sb-prepend",
						0
					],
					"source": [
						"obj-sb-active-gate",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-sb-udpsend",
						0
					],
					"source": [
						"obj-sb-prepend",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-sb-sprintf",
						0
					],
					"source": [
						"obj-param-name",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-sb-prepend",
						0
					],
					"source": [
						"obj-sb-sprintf",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-sb-port-msg",
						0
					],
					"source": [
						"obj-dest-port",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-sb-udpsend",
						0
					],
					"source": [
						"obj-sb-port-msg",
						0
					]
				}
			}
		],
		"parameters": {
			"obj-11": [
				"Gain",
				"Gain",
				0
			],
			"obj-14::obj-22": [
				"Mix",
				"Mix",
				0
			],
			"obj-14::obj-30": [
				"Sidechain",
				"Sidechain",
				0
			],
			"obj-19": [
				"Delay",
				"Delay",
				0
			],
			"obj-24": [
				"live.text",
				"live.text",
				0
			],
			"obj-25": [
				"ShowMod",
				"Mappings",
				0
			],
			"obj-27::obj-23": [
				"Show Multimap[3]",
				"Multimap",
				0
			],
			"obj-27::obj-25::obj-103": [
				"border[12]",
				"border",
				0
			],
			"obj-27::obj-25::obj-2": [
				"mode[7]",
				"Modulation",
				0
			],
			"obj-27::obj-25::obj-25": [
				"Map[13]",
				"Map",
				0
			],
			"obj-27::obj-25::obj-26": [
				"border[7]",
				"border",
				0
			],
			"obj-27::obj-25::obj-30": [
				"Unmap[11]",
				"Unmap",
				0
			],
			"obj-27::obj-25::obj-32": [
				"TargetMax[6]",
				"Max",
				0
			],
			"obj-27::obj-25::obj-33": [
				"TargetMin[4]",
				"Min",
				0
			],
			"obj-27::obj-25::obj-6": [
				"Modulation Polarity 2",
				"Polarity",
				0
			],
			"obj-27::obj-25::obj-9": [
				"Modulation Amount 2",
				"ModAmount",
				0
			],
			"obj-27::obj-26::obj-103": [
				"border[1]",
				"border",
				0
			],
			"obj-27::obj-26::obj-2": [
				"mode[6]",
				"Modulation",
				0
			],
			"obj-27::obj-26::obj-25": [
				"Map[1]",
				"Map",
				0
			],
			"obj-27::obj-26::obj-26": [
				"border[2]",
				"border",
				0
			],
			"obj-27::obj-26::obj-30": [
				"Unmap[2]",
				"Unmap",
				0
			],
			"obj-27::obj-26::obj-32": [
				"TargetMax[5]",
				"Max",
				0
			],
			"obj-27::obj-26::obj-33": [
				"TargetMin[13]",
				"Min",
				0
			],
			"obj-27::obj-26::obj-6": [
				"Modulation Polarity 3",
				"Polarity",
				0
			],
			"obj-27::obj-26::obj-9": [
				"Modulation Amount 3",
				"ModAmount",
				0
			],
			"obj-27::obj-27::obj-103": [
				"border[3]",
				"border",
				0
			],
			"obj-27::obj-27::obj-2": [
				"mode[5]",
				"Modulation",
				0
			],
			"obj-27::obj-27::obj-25": [
				"Map[2]",
				"Map",
				0
			],
			"obj-27::obj-27::obj-26": [
				"border[8]",
				"border",
				0
			],
			"obj-27::obj-27::obj-30": [
				"Unmap[12]",
				"Unmap",
				0
			],
			"obj-27::obj-27::obj-32": [
				"TargetMax[4]",
				"Max",
				0
			],
			"obj-27::obj-27::obj-33": [
				"TargetMin[12]",
				"Min",
				0
			],
			"obj-27::obj-27::obj-6": [
				"Modulation Polarity 4",
				"Polarity",
				0
			],
			"obj-27::obj-27::obj-9": [
				"Modulation Amount 4",
				"ModAmount",
				0
			],
			"obj-27::obj-29::obj-103": [
				"border[9]",
				"border",
				0
			],
			"obj-27::obj-29::obj-2": [
				"mode[4]",
				"Modulation",
				0
			],
			"obj-27::obj-29::obj-25": [
				"Map[3]",
				"Map",
				0
			],
			"obj-27::obj-29::obj-26": [
				"border[13]",
				"border",
				0
			],
			"obj-27::obj-29::obj-30": [
				"Unmap[14]",
				"Unmap",
				0
			],
			"obj-27::obj-29::obj-32": [
				"TargetMax[3]",
				"Max",
				0
			],
			"obj-27::obj-29::obj-33": [
				"TargetMin[3]",
				"Min",
				0
			],
			"obj-27::obj-29::obj-6": [
				"Modulation Polarity 5",
				"Polarity",
				0
			],
			"obj-27::obj-29::obj-9": [
				"Modulation Amount 5",
				"ModAmount",
				0
			],
			"obj-27::obj-30::obj-103": [
				"border[5]",
				"border",
				0
			],
			"obj-27::obj-30::obj-2": [
				"mode[3]",
				"Modulation",
				0
			],
			"obj-27::obj-30::obj-25": [
				"Map[14]",
				"Map",
				0
			],
			"obj-27::obj-30::obj-26": [
				"border[4]",
				"border",
				0
			],
			"obj-27::obj-30::obj-30": [
				"Unmap[21]",
				"Unmap",
				0
			],
			"obj-27::obj-30::obj-32": [
				"TargetMax[2]",
				"Max",
				0
			],
			"obj-27::obj-30::obj-33": [
				"TargetMin[2]",
				"Min",
				0
			],
			"obj-27::obj-30::obj-6": [
				"Modulation Polarity 6",
				"Polarity",
				0
			],
			"obj-27::obj-30::obj-9": [
				"Modulation Amount 6",
				"ModAmount",
				0
			],
			"obj-27::obj-33::obj-103": [
				"border[14]",
				"border",
				0
			],
			"obj-27::obj-33::obj-2": [
				"mode[2]",
				"Modulation",
				0
			],
			"obj-27::obj-33::obj-25": [
				"Map[4]",
				"Map",
				0
			],
			"obj-27::obj-33::obj-26": [
				"border[10]",
				"border",
				0
			],
			"obj-27::obj-33::obj-30": [
				"Unmap[5]",
				"Unmap",
				0
			],
			"obj-27::obj-33::obj-32": [
				"TargetMax[1]",
				"Max",
				0
			],
			"obj-27::obj-33::obj-33": [
				"TargetMin[1]",
				"Min",
				0
			],
			"obj-27::obj-33::obj-6": [
				"Modulation Polarity 7",
				"Polarity",
				0
			],
			"obj-27::obj-33::obj-9": [
				"Modulation Amount 7",
				"ModAmount",
				0
			],
			"obj-27::obj-34::obj-103": [
				"border[15]",
				"border",
				0
			],
			"obj-27::obj-34::obj-2": [
				"mode[1]",
				"Modulation",
				0
			],
			"obj-27::obj-34::obj-25": [
				"Map[5]",
				"Map",
				0
			],
			"obj-27::obj-34::obj-26": [
				"border[11]",
				"border",
				0
			],
			"obj-27::obj-34::obj-30": [
				"Unmap[6]",
				"Unmap",
				0
			],
			"obj-27::obj-34::obj-32": [
				"TargetMax[11]",
				"Max",
				0
			],
			"obj-27::obj-34::obj-33": [
				"TargetMin[11]",
				"Min",
				0
			],
			"obj-27::obj-34::obj-6": [
				"Modulation Polarity 8",
				"Polarity",
				0
			],
			"obj-27::obj-34::obj-9": [
				"Modulation Amount 8",
				"ModAmount",
				0
			],
			"obj-38": [
				"Delay Mode",
				"Delay Mode",
				1
			],
			"obj-3::obj-103": [
				"border[17]",
				"border",
				0
			],
			"obj-3::obj-2": [
				"mode[11]",
				"Modulation",
				0
			],
			"obj-3::obj-25": [
				"Map[15]",
				"Map",
				0
			],
			"obj-3::obj-26": [
				"border[16]",
				"border",
				0
			],
			"obj-3::obj-30": [
				"Unmap[7]",
				"Unmap",
				0
			],
			"obj-3::obj-32": [
				"TargetMax[7]",
				"Max",
				0
			],
			"obj-3::obj-33": [
				"TargetMin[5]",
				"Min",
				0
			],
			"obj-3::obj-6": [
				"Modulation Polarity 1",
				"Polarity",
				0
			],
			"obj-3::obj-9": [
				"Modulation Amount 1",
				"ModAmount",
				0
			],
			"obj-49": [
				"Delay Synced",
				"Delay",
				0
			],
			"obj-77": [
				"Rise",
				"Rise",
				0
			],
			"obj-81": [
				"Fall",
				"Fall",
				0
			],
			"parameterbanks": {
				"0": {
					"index": 0,
					"name": "Main",
					"parameters": [
						"-",
						"-",
						"-",
						"Rise",
						"Fall",
						"Delay Mode",
						"Delay",
						"Gain"
					]
				}
			},
			"parameter_overrides": {
				"obj-14::obj-30": {
					"parameter_initial": 0,
					"parameter_initial_enable": 1
				},
				"obj-27::obj-25::obj-103": {
					"parameter_longname": "border[12]"
				},
				"obj-27::obj-25::obj-2": {
					"parameter_longname": "mode[7]"
				},
				"obj-27::obj-25::obj-25": {
					"parameter_longname": "Map[13]"
				},
				"obj-27::obj-25::obj-26": {
					"parameter_longname": "border[7]"
				},
				"obj-27::obj-25::obj-30": {
					"parameter_longname": "Unmap[11]"
				},
				"obj-27::obj-25::obj-32": {
					"parameter_longname": "TargetMax[6]"
				},
				"obj-27::obj-25::obj-33": {
					"parameter_longname": "TargetMin[4]"
				},
				"obj-27::obj-25::obj-6": {
					"parameter_longname": "Modulation Polarity 2"
				},
				"obj-27::obj-25::obj-9": {
					"parameter_longname": "Modulation Amount 2"
				},
				"obj-27::obj-26::obj-103": {
					"parameter_longname": "border[1]"
				},
				"obj-27::obj-26::obj-2": {
					"parameter_longname": "mode[6]"
				},
				"obj-27::obj-26::obj-25": {
					"parameter_longname": "Map[1]"
				},
				"obj-27::obj-26::obj-26": {
					"parameter_longname": "border[2]"
				},
				"obj-27::obj-26::obj-30": {
					"parameter_longname": "Unmap[2]"
				},
				"obj-27::obj-26::obj-32": {
					"parameter_longname": "TargetMax[5]"
				},
				"obj-27::obj-26::obj-33": {
					"parameter_longname": "TargetMin[13]"
				},
				"obj-27::obj-26::obj-6": {
					"parameter_longname": "Modulation Polarity 3"
				},
				"obj-27::obj-26::obj-9": {
					"parameter_longname": "Modulation Amount 3"
				},
				"obj-27::obj-27::obj-103": {
					"parameter_longname": "border[3]"
				},
				"obj-27::obj-27::obj-2": {
					"parameter_longname": "mode[5]"
				},
				"obj-27::obj-27::obj-25": {
					"parameter_longname": "Map[2]"
				},
				"obj-27::obj-27::obj-26": {
					"parameter_longname": "border[8]"
				},
				"obj-27::obj-27::obj-30": {
					"parameter_longname": "Unmap[12]"
				},
				"obj-27::obj-27::obj-32": {
					"parameter_longname": "TargetMax[4]"
				},
				"obj-27::obj-27::obj-33": {
					"parameter_longname": "TargetMin[12]"
				},
				"obj-27::obj-27::obj-6": {
					"parameter_longname": "Modulation Polarity 4"
				},
				"obj-27::obj-27::obj-9": {
					"parameter_longname": "Modulation Amount 4"
				},
				"obj-27::obj-29::obj-103": {
					"parameter_longname": "border[9]"
				},
				"obj-27::obj-29::obj-2": {
					"parameter_longname": "mode[4]"
				},
				"obj-27::obj-29::obj-25": {
					"parameter_longname": "Map[3]"
				},
				"obj-27::obj-29::obj-26": {
					"parameter_longname": "border[13]"
				},
				"obj-27::obj-29::obj-30": {
					"parameter_longname": "Unmap[14]"
				},
				"obj-27::obj-29::obj-32": {
					"parameter_longname": "TargetMax[3]"
				},
				"obj-27::obj-29::obj-33": {
					"parameter_longname": "TargetMin[3]"
				},
				"obj-27::obj-29::obj-6": {
					"parameter_longname": "Modulation Polarity 5"
				},
				"obj-27::obj-29::obj-9": {
					"parameter_longname": "Modulation Amount 5"
				},
				"obj-27::obj-30::obj-103": {
					"parameter_longname": "border[5]"
				},
				"obj-27::obj-30::obj-2": {
					"parameter_longname": "mode[3]"
				},
				"obj-27::obj-30::obj-25": {
					"parameter_longname": "Map[14]"
				},
				"obj-27::obj-30::obj-26": {
					"parameter_longname": "border[4]"
				},
				"obj-27::obj-30::obj-30": {
					"parameter_longname": "Unmap[21]"
				},
				"obj-27::obj-30::obj-32": {
					"parameter_longname": "TargetMax[2]"
				},
				"obj-27::obj-30::obj-33": {
					"parameter_longname": "TargetMin[2]"
				},
				"obj-27::obj-30::obj-6": {
					"parameter_longname": "Modulation Polarity 6"
				},
				"obj-27::obj-30::obj-9": {
					"parameter_longname": "Modulation Amount 6"
				},
				"obj-27::obj-33::obj-103": {
					"parameter_longname": "border[14]"
				},
				"obj-27::obj-33::obj-2": {
					"parameter_longname": "mode[2]"
				},
				"obj-27::obj-33::obj-25": {
					"parameter_longname": "Map[4]"
				},
				"obj-27::obj-33::obj-26": {
					"parameter_longname": "border[10]"
				},
				"obj-27::obj-33::obj-30": {
					"parameter_longname": "Unmap[5]"
				},
				"obj-27::obj-33::obj-32": {
					"parameter_longname": "TargetMax[1]"
				},
				"obj-27::obj-33::obj-33": {
					"parameter_longname": "TargetMin[1]"
				},
				"obj-27::obj-33::obj-6": {
					"parameter_longname": "Modulation Polarity 7"
				},
				"obj-27::obj-33::obj-9": {
					"parameter_longname": "Modulation Amount 7"
				},
				"obj-27::obj-34::obj-103": {
					"parameter_longname": "border[15]"
				},
				"obj-27::obj-34::obj-2": {
					"parameter_longname": "mode[1]"
				},
				"obj-27::obj-34::obj-25": {
					"parameter_longname": "Map[5]"
				},
				"obj-27::obj-34::obj-26": {
					"parameter_longname": "border[11]"
				},
				"obj-27::obj-34::obj-30": {
					"parameter_longname": "Unmap[6]"
				},
				"obj-27::obj-34::obj-32": {
					"parameter_longname": "TargetMax[11]"
				},
				"obj-27::obj-34::obj-33": {
					"parameter_longname": "TargetMin[11]"
				},
				"obj-27::obj-34::obj-6": {
					"parameter_longname": "Modulation Polarity 8"
				},
				"obj-27::obj-34::obj-9": {
					"parameter_longname": "Modulation Amount 8"
				},
				"obj-3::obj-103": {
					"parameter_longname": "border[17]"
				},
				"obj-3::obj-2": {
					"parameter_longname": "mode[11]"
				},
				"obj-3::obj-25": {
					"parameter_longname": "Map[15]"
				},
				"obj-3::obj-26": {
					"parameter_longname": "border[16]"
				},
				"obj-3::obj-30": {
					"parameter_longname": "Unmap[7]"
				},
				"obj-3::obj-32": {
					"parameter_longname": "TargetMax[7]"
				},
				"obj-3::obj-33": {
					"parameter_longname": "TargetMin[5]"
				},
				"obj-3::obj-6": {
					"parameter_longname": "Modulation Polarity 1"
				},
				"obj-3::obj-9": {
					"parameter_longname": "Modulation Amount 1"
				}
			},
			"inherited_shortname": 1,
			"obj-param-name": [
				"Param Name",
				"Param",
				0
			],
			"obj-active": [
				"Active",
				"Active",
				0
			],
			"obj-sb-gate-dial": [
				"Gate",
				"Gate",
				0
			],
			"obj-invert": [
				"Invert",
				"Inv",
				0
			],
			"obj-dest-port": [
				"Dest Port",
				"Port",
				0
			]
		},
		"dependency_cache": [
			{
				"name": "Abl.Map.maxpat",
				"bootpath": "~/Documents/Max 9/Max for Live Devices/Envelope Follower Project",
				"type": "JSON",
				"implicit": 1
			},
			{
				"name": "Abl.MapUi.maxpat",
				"bootpath": "~/Documents/Max 9/Max for Live Devices/Envelope Follower Project",
				"type": "JSON",
				"implicit": 1
			},
			{
				"name": "Abl.MultiMap.maxpat",
				"bootpath": "~/Documents/Max 9/Max for Live Devices/Envelope Follower Project",
				"type": "JSON",
				"implicit": 1
			},
			{
				"name": "M4L.bal2~.maxpat",
				"bootpath": "C74:/patchers/m4l/Tools resources",
				"type": "JSON",
				"implicit": 1
			},
			{
				"name": "Polarity_PlusLarge.svg",
				"bootpath": "~/Documents/Max 9/Max for Live Devices/Envelope Follower Project",
				"type": "svg",
				"implicit": 1
			},
			{
				"name": "Polarity_PlusMinusLarge.svg",
				"bootpath": "~/Documents/Max 9/Max for Live Devices/Envelope Follower Project",
				"type": "svg",
				"implicit": 1
			},
			{
				"name": "audio-rg.svg",
				"bootpath": "~/Documents/Max 9/Max for Live Devices/Envelope Follower Project",
				"type": "svg",
				"implicit": 1
			},
			{
				"name": "beat-icon.svg",
				"bootpath": "~/Documents/Max 9/Max for Live Devices/Envelope Follower Project",
				"type": "svg",
				"implicit": 1
			},
			{
				"name": "getObjectRect.js",
				"bootpath": "~/Documents/Max 9/Max for Live Devices/Envelope Follower Project",
				"type": "TEXT",
				"implicit": 1
			},
			{
				"name": "moveUi.js",
				"bootpath": "~/Documents/Max 9/Max for Live Devices/Envelope Follower Project",
				"type": "TEXT",
				"implicit": 1
			},
			{
				"name": "ms-icon.svg",
				"bootpath": "~/Documents/Max 9/Max for Live Devices/Envelope Follower Project",
				"type": "svg",
				"implicit": 1
			},
			{
				"name": "multimap-closed-off.svg",
				"bootpath": "~/Documents/Max 9/Max for Live Devices/Envelope Follower Project",
				"type": "svg",
				"implicit": 1
			},
			{
				"name": "multimap-open-off.svg",
				"bootpath": "~/Documents/Max 9/Max for Live Devices/Envelope Follower Project",
				"type": "svg",
				"implicit": 1
			},
			{
				"name": "multimap-unmap.svg",
				"bootpath": "~/Documents/Max 9/Max for Live Devices/Envelope Follower Project",
				"type": "svg",
				"implicit": 1
			},
			{
				"name": "sr-arrow-down-11x11.svg",
				"bootpath": "~/Documents/Max 9/Max for Live Devices/Envelope Follower Project",
				"type": "svg",
				"implicit": 1
			},
			{
				"name": "sr-arrow-right-11x11.svg",
				"bootpath": "~/Documents/Max 9/Max for Live Devices/Envelope Follower Project",
				"type": "svg",
				"implicit": 1
			}
		],
		"latency": 0,
		"is_mpe": 0,
		"external_mpe_tuning_enabled": 0,
		"minimum_live_version": "12.0",
		"minimum_max_version": "8.5.6",
		"platform_compatibility": 0,
		"project": {
			"version": 1,
			"creationdate": 3587469966,
			"modificationdate": 3688459081,
			"viewrect": [
				595.0,
				96.0,
				300.0,
				500.0
			],
			"autoorganize": 0,
			"hideprojectwindow": 1,
			"showdependencies": 1,
			"autolocalize": 0,
			"contents": {
				"patchers": {},
				"media": {
					"Polarity_MinusLarge.svg": {
						"kind": "vectorimagefile",
						"local": 1
					},
					"Polarity_PlusLarge.svg": {
						"kind": "vectorimagefile",
						"local": 1
					},
					"Polarity_PlusMinusLarge.svg": {
						"kind": "vectorimagefile",
						"local": 1
					}
				},
				"code": {}
			},
			"layout": {},
			"searchpath": {},
			"detailsvisible": 1,
			"amxdtype": 1633771873,
			"readonly": 1,
			"devpathtype": 0,
			"devpath": ".",
			"sortmode": 0,
			"viewmode": 0,
			"includepackages": 0
		},
		"autosave": 0,
		"saved_attribute_attributes": {
			"default_plcolor": {
				"expression": ""
			}
		},
		"oscreceiveudpport": 0,
		"devicewidth": 280.0,
		"description": "Envelope Follower OSC Bridge. Follows audio amplitude and sends normalized 0-1 floats over OSC.",
		"digest": "Envelope follower with OSC export.",
		"tags": "signal osc envelope"
	}
}