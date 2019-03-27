::: {.cell .code execution_count="1"}
``` {.python}
# This notebook is a semi top-down explanation. This cell needs to be
# executed first so that the operators and helper functions are defined
# All of this is explained in the later half of the notebook

using Compose, Interact
Compose.set_default_graphic_size(2inch, 2inch)

points_f = [
    (.1, .1),
    (.9, .1),
    (.9, .2),
    (.2, .2),
    (.2, .4),
    (.6, .4),
    (.6, .5),
    (.2, .5),
    (.2, .9),
    (.1, .9),
    (.1, .1)
]

f = compose(context(), stroke("black"), line(points_f))

rot(pic) = compose(context(rotation=Rotation(-deg2rad(90))), pic)
flip(pic) = compose(context(mirror=Mirror(deg2rad(90), 0.5w, 0.5h)), pic)
above(m, n, p, q) =
    compose(context(),
            (context(0, 0, 1, m/(m+n)), p),
            (context(0, m/(m+n), 1, n/(m+n)), q))

above(p, q) = above(1, 1, p, q)

beside(m, n, p, q) =
    compose(context(),
            (context(0, 0, m/(m+n), 1), p),
            (context(m/(m+n), 0, n/(m+n), 1), q))

beside(p, q) = beside(1, 1, p, q)

over(p, q) = compose(context(),
                (context(), p), (context(), q))

rot45(pic) =
    compose(context(0, 0, 1/sqrt(2), 1/sqrt(2),
        rotation=Rotation(-deg2rad(45), 0w, 0h)), pic)

# Utility function to zoom out and look at the context
zoomout(pic) = compose(context(),
                (context(0.2, 0.2, 0.6, 0.6), pic),
                (context(0.2, 0.2, 0.6, 0.6), fill(nothing), stroke("black"), strokedash([0.5mm, 0.5mm]),
                    polygon([(0, 0), (1, 0), (1, 1), (0, 1)])))

function read_path(p_str)
    tokens = [try parsefloat(x) catch symbol(x) end for x in split(p_str, r"[\s,]+")]
    path(tokens)
end

fish = compose(context(units=UnitBox(260, 260)), stroke("black"),
            read_path(strip(readall("fish.path"))))

rotatable(pic) = @manipulate for θ=0:0.001:2π
    compose(context(rotation=Rotation(θ)), pic)
end

blank = compose(context())

fliprot45(pic) = rot45(compose(context(mirror=Mirror(deg2rad(-45))),pic))

# Hide this cell.
display(MIME("text/html"), """<script>
var cell = \$(".container .cell").eq(0), ia = cell.find(".input_area")
if (cell.find(".toggle-button").length == 0) {
ia.after(
    \$('<button class="toggle-button">Toggle hidden code</button>').click(
        function (){ ia.toggle() }
        )
    )
ia.hide()
}
</script>""")
```

::: {.output .display_data}
<script charset="utf-8">(function ($, undefined) {

    function createElem(tag, attr, content) {
	// TODO: remove jQuery dependency
	var el = $("<" + tag + "/>").attr(attr);
	if (content) {
	    el.append(content);
	}
	return el[0];
    }

    // A widget must expose an id field which identifies it to the backend,
    // an elem attribute which is will be added to the DOM, and
    // a getState() method which returns the value to be sent to the backend
    // a sendUpdate() method which sends its current value to the backend
    var Widget = {
	id: undefined,
	elem: undefined,
	label: undefined,
	getState: function () {
	    return this.elem.value;
	},
	sendUpdate: undefined
    };

    var Slider = function (typ, id, init) {
	var attr = { type:  "range",
		     value: init.value,
		     min:   init.min,
		     max:   init.max,
		     step:  init.step },
	    elem = createElem("input", attr),
	    self = this;

	elem.onchange = function () {
	    self.sendUpdate();
	}

	this.id = id;
	this.elem = elem;
	this.label = init.label;

	InputWidgets.commInitializer(this); // Initialize communication
    }
    Slider.prototype = Widget;

    var Checkbox = function (typ, id, init) {
	var attr = { type: "checkbox",
		     checked: init.value },
	    elem = createElem("input", attr),
	    self = this;

	this.getState = function () {
	    return elem.checked;
	}
	elem.onchange = function () {
	    self.sendUpdate();
	}

	this.id = id;
	this.elem = elem;
	this.label = init.label;

	InputWidgets.commInitializer(this);
    }
    Checkbox.prototype = Widget;

    var Button = function (typ, id, init) {
	var attr = { type:    "button",
		     value:   init.label },
	    elem = createElem("input", attr),
	    self = this;
	this.getState = function () {
	    return null;
	}
	elem.onclick = function () {
	    self.sendUpdate();
	}

	this.id = id;
	this.elem = elem;
	this.label = init.label;

	InputWidgets.commInitializer(this);
    }
    Button.prototype = Widget;

    var Text = function (typ, id, init) {
	var attr = { type:  "text",
		     placeholder: init.label,
		     value: init.value },
	    elem = createElem("input", attr),
	    self = this;
	this.getState = function () {
	    return elem.value;
	}
	elem.onkeyup = function () {
	    self.sendUpdate();
	}

	this.id = id;
	this.elem = elem;
	this.label = init.label;

	InputWidgets.commInitializer(this);
    }
    Text.prototype = Widget;

    var Textarea = function (typ, id, init) {
	var attr = { placeholder: init.label },
	    elem = createElem("textarea", attr, init.value),
	    self = this;
	this.getState = function () {
	    return elem.value;
	}
	elem.onchange = function () {
	    self.sendUpdate();
	}

	this.id = id;
	this.elem = elem;
	this.label = init.label;

	InputWidgets.commInitializer(this);
    }
    Textarea.prototype = Widget;

    // RadioButtons
    // Dropdown
    // HTML
    // Latex

    var InputWidgets = {
	Slider: Slider,
	Checkbox: Checkbox,
	Button: Button,
	Text: Text,
	Textarea: Textarea,
	debug: false,
	log: function () {
	    if (InputWidgets.debug) {
		console.log.apply(console, arguments);
	    }
	},
	// a central way to initalize communication
	// for widgets.
	commInitializer: function (widget) {
	    widget.sendUpdate = function () {};
	}
    };

    window.InputWidgets = InputWidgets;

})(jQuery, undefined);
</script>
:::

::: {.output .display_data}
<script charset="utf-8">(function (IPython, $, _, MathJax, Widgets) {
    $.event.special.destroyed = {
	remove: function(o) {
	    if (o.handler) {
		o.handler.apply(this, arguments)
	    }
	}
    }

    var redrawValue = function (container, type, val) {
	var selector = $("<div/>");
	var oa = new IPython.OutputArea(_.extend(selector, {
	    selector: selector,
	    prompt_area: true,
	    events: IPython.events,
	    keyboard_manager: IPython.keyboard_manager
	})); // Hack to work with IPython 2.1.0

	switch (type) {
	case "image/png":
            var _src = 'data:' + type + ';base64,' + val;
	    $(container).find("img").attr('src', _src);
	    break;
	default:
	    var toinsert = IPython.OutputArea.append_map[type].apply(
		oa, [val, {}, selector]
	    );
	    $(container).empty().append(toinsert.contents());
	    selector.remove();
	}
	if (type === "text/latex" && MathJax) {
	    MathJax.Hub.Queue(["Typeset", MathJax.Hub, toinsert.get(0)]);
	}
    }


    $(document).ready(function() {
	Widgets.debug = false; // log messages etc in console.
	function initComm(evt, data) {
	    var comm_manager = data.kernel.comm_manager;
	    comm_manager.register_target("Signal", function (comm) {
		comm.on_msg(function (msg) {
		    //Widgets.log("message received", msg);
		    var val = msg.content.data.value;
		    $(".signal-" + comm.comm_id).each(function() {
			var type = $(this).data("type");
			if (val[type]) {
			    redrawValue(this, type, val[type], type);
			}
		    });
		    delete val;
		    delete msg.content.data.value;
		});
	    });

	    // coordingate with Comm and redraw Signals
	    // XXX: Test using Reactive here to improve performance
	    $([IPython.events]).on(
		'output_appended.OutputArea', function (event, type, value, md, toinsert) {
		    if (md && md.reactive) {
			// console.log(md.comm_id);
			toinsert.addClass("signal-" + md.comm_id);
			toinsert.data("type", type);
			// Signal back indicating the mimetype required
			var comm_manager = IPython.notebook.kernel.comm_manager;
			var comm = comm_manager.comms[md.comm_id];
			comm.send({action: "subscribe_mime",
				   mime: type});
			toinsert.bind("destroyed", function() {
			    comm.send({action: "unsubscribe_mime",
				       mime: type});
			});
		    }
	    });

	    // Set up communication for Widgets
	    Widgets.commInitializer = function (widget) {
		var comm = comm_manager.new_comm(
		    "InputWidget", {widget_id: widget.id}
		);
		widget.sendUpdate = function () {
		    // `this` is a widget here.
		    // TODO: I have a feeling there's some
		    //       IPython bookkeeping to be done here.
		    // Widgets.log("State changed", this, this.getState());
		    comm.send({value: this.getState()});
		}
	    };
	}

	try {
	    // try to initialize right away. otherwise, wait on the status_started event.
	    initComm(undefined, IPython.notebook);
	} catch (e) {
	    $([IPython.events]).on('status_started.Kernel', initComm);
	}
    });
})(IPython, jQuery, _, MathJax, InputWidgets);
</script>
:::

::: {.output .display_data}
<script>
var cell = $(".container .cell").eq(0), ia = cell.find(".input_area")
if (cell.find(".toggle-button").length == 0) {
ia.after(
    $('<button class="toggle-button">Toggle hidden code</button>').click(
        function (){ ia.toggle() }
        )
    )
ia.hide()
}
</script>
:::
:::

::: {.cell .markdown}
# Functional Geometry

*Functional Geometry* is a paper by Peter Henderson ([original
(1982)](users.ecs.soton.ac.uk/peter/funcgeo.pdf), [revisited
(2002)](https://cs.au.dk/~hosc/local/HOSC-15-4-pp349-365.pdf)) which
deconstructs the MC Escher woodcut *Square Limit*

![Square Limit](http://i.imgur.com/LjRzmNM.png)
:::

::: {.cell .markdown}
> A picture is an example of a complex object that can be described in
> terms of its parts. Yet a picture needs to be rendered on a printer or
> a screen by a device that expects to be given a sequence of commands.
> Programming that sequence of commands directly is much harder than
> having an application generate the commands automatically from the
> simpler, denotational description.
:::

::: {.cell .markdown}
A `picture` is a *denotation* of something to draw.

e.g. The value of f here denotes the picture of the letter F
:::

::: {.cell .markdown}
Original at
<http://nbviewer.jupyter.org/github/shashi/ijulia-notebooks/blob/master/funcgeo/Functional%20Geometry.ipynb>
:::

::: {.cell .markdown}
## In conclusion

We described Escher\'s *Square Limit* from the description of its
smaller parts, which in turn were described in terms of their smaller
parts.

This seemed simple because we chose to talk in terms of an *algebra* to
describe pictures. The primitives `rot`, `flip`, `fliprot45`, `above`,
`beside` and `over` fit the job perfectly.

We were able to describe these primitves in terms of `compose`
`contexts`, which the Compose library knows how to render.

Denotation can be an easy way to describe a system as well as a
practical implementation method.

[Abstraction
barriers](https://mitpress.mit.edu/sicp/full-text/sicp/book/node29.html)
are useful tools that can reduce the cognitive overhead on the
programmer. It entails creating layers consisting of functions which
only use functions in the same layer or layers below in their own
implementation. The layers in our language were:

    ------------------[ squarelimit ]------------------
    -------------[ quartet, cycle, nonet ]-------------
    ---[ rot, flip, fliprot45, above, beside, over ]---
    -------[ compose, context, line, path,... ]--------

Drawing this diagram out is a useful way to begin building any library.
:::
