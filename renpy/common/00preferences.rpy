# Copyright 2004-2015 Tom Rothamel <pytom@bishoujo.us>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

init -1500 python:

    ## data structure

    __preferences = {}
    # __preferences[name] = {
    #     "choices": [possible choices],
    #     "takes_float": bool,
    #     "takes_int": bool,
    #     "callfunc": function_to_call }


    ## insertion into data structure

    @renpy.pure
    def __registerPreference( name,
                              callfunc,
                              choices = (),
                              takes_float = False,
                              takes_int = False ):
        
        assert not __preferences.has_key(name)
        __preferences[name] = { "choices": choices,
                                "takes_float": takes_float,
                                "takes_int": takes_int,
                                "callfunc": callfunc }


    @renpy.pure
    def __registerToggle(name,field):

        def f(value,field=field):
            if value == "enable":
                return SetField(_preferences, field, True)
            if value == "disable":
                return SetField(_preferences, field, False)
            return ToggleField(_preferences, field)

        __registerPreference(name,f,choices=("enable","disable","toggle"))
                          

    @renpy.pure
    def __registerDToggle(name,d,field):

        def f(value,d=d,field=field):
            if value == "enable":
                return SetDict(d, field, True)
            if value == "disable":
                return SetDict(d, field, False)
            return ToggleDict(d, field)

        __registerPreference(name,f,choices=("enable","disable","toggle"))
                          

    @renpy.pure
    def __registerMixer(name,mxr):

        def f(value,mxr=mxr):
            if value is None:
                return MixerValue(mxr)
            else:
                return SetMixer(mxr,value)

        __registerPreference(name,f)


    ## system preferences

    @renpy.pure
    class __DisplayAction(Action, DictEquality):
        def __init__(self, factor):
            self.width = int(factor * config.screen_width)
            self.height = int(factor * config.screen_height)

        def __call__(self):
            renpy.set_physical_size((self.width, self.height))
            renpy.restart_interaction()

        def get_sensitive(self):
            if self.width == config.screen_width and self.height == config.screen_height:
                return True

            return renpy.get_renderer_info()["resizable"]

        def get_selected(self):
            if _preferences.fullscreen:
                return False

            return (self.width, self.height) == renpy.get_physical_size()

    _m1_00screen__DisplayAction = __DisplayAction

    def __p_display(value):
        if value == "fullscreen":
            return SetField(_preferences, "fullscreen", True)
        if value == "window":
            return __DisplayAction(1.0)
        if value == "any window":
            return SetField(_preferences, "fullscreen", False)
        if isinstance(value, (int, float)):
            return __DisplayAction(value)
        return ToggleField(_preferences, "fullscreen")

    __registerPreference( "display",
                          callfunc = __p_display,
                          choices = ("fullscreen","window","any window","toggle"),
                          takes_float = True,
                          takes_int = True )


    def __p_transitions(value):
        if value == "all":
            return SetField(_preferences, "transitions", 2)
        if value == "some":
            return SetField(_preferences, "transitions", 1)
        if value == "none":
            return SetField(_preferences, "transitions", 0)
        return ToggleField(_preferences, "transitions", true_value=2, false_value=0)

    __registerPreference( "transitions",
                          callfunc = __p_transitions,
                          choices=("all","some","none","toggle") )


    def __p_show_empty_window(value):
        if value == "show":
            return SetField(_preferences, "show_empty_window", True)
        if value == "hide":
            return SetField(_preferences, "show_empty_window", False)
        return ToggleField(_preferences, "show_empty_window")

    __registerPreference( "show empty window",
                          callfunc = __p_show_empty_window,
                          choices = ("show","hide","toggle") )


    def __p_text_speed(value):
        if value is None:
            return FieldValue(_preferences, "text_cps", range=200, max_is_zero=True, style="slider")
        if isinstance(value, int):
            return SetField(_preferences, "text_cps", value)

    __registerPreference( "text speed",
                          callfunc = __p_text_speed )

                          
    config.always_has_joystick = False

    def __p_joystick(value):
        if renpy.display.joystick.enabled or config.always_has_joystick:
            return ShowMenu("joystick_preferences")
        return None
        
    __registerPreference( "joystick",
                          callfunc = __p_joystick )
    __registerPreference( "joystick...",
                          callfunc = __p_joystick )


    def __p_skip(value):
        if value == "all messages" or value == "all":
            return SetField(_preferences, "skip_unseen", True)
        if value == "seen messages" or value == "seen":
            return SetField(_preferences, "skip_unseen", False)
        return ToggleField(_preferences, "skip_unseen")

    __registerPreference( "skip",
                          callfunc = __p_skip,
                          choices = ( "all","all messages",
                                      "seen","seen_messages",
                                      "toggle" ) )

    __registerPreference("begin skipping",lambda x: Skip())


    def __p_after_choices(value):
        if value == "keep skipping" or value == "keep" or value == "skip":
            return SetField(_preferences, "skip_after_choices", True)
        if value == "stop skipping" or value == "stop":
            return SetField(_preferences, "skip_after_choices", False)
        return ToggleField(_preferences, "skip_after_choices")

    __registerPreference( "after choices",
                          callfunc = __p_after_choices,
                          choices = ( "skip","keep","keep skipping",
                                      "stop","stop_skipping",
                                      "toggle" ) )


    def __p_auto_forward_time(value):
        if value is None:

            if config.default_afm_enable is None:
                return FieldValue(_preferences, "afm_time", range=30.0, max_is_zero=True, style="slider")
            return FieldValue(_preferences, "afm_time", range=29.9, style="slider", offset=.1)

        elif isinstance(value, int):
            return SetField(_preferences, "afm_time", value)

    __registerPreference( "auto-forward time",
                          callfunc = __p_auto_forward_time )


    __registerToggle("auto-forward","afm_enable")
    __registerToggle("auto-forward_after_click","afm_after_click")
    __registerToggle("automatic move","mouse_move")
    __registerToggle("wait for voice","wait_voice")

    __registerMixer("music volume","music")
    __registerMixer("sound volume","sfx")
    __registerMixer("voice volume","voice")

    __registerDToggle("music mute",_preferences.mute,"music")
    __registerDToggle("sound mute",_preferences.mute,"sfx")
    __registerDToggle("voice mute",_preferences.mute,"voice")

    __registerToggle("voice sustain","voice_sustain")
    __registerToggle("self voicing","self_voicing")


    def __p_clipboard_voicing(value):
        if value == "enable":
            return SetField(_preferences, "self_voicing", "clipboard")
        if value == "disable":
            return SetField(_preferences, "self_voicing", False)
        return ToggleField(_preferences, "self_voicing", true_value="clipboard")

    __registerPreference( "clipboard voicing",
                          callfunc = __p_clipboard_voicing,
                          choices = ("enable","disable","toggle") )


    __registerToggle("emphasize audio","emphasize_audio")


    ## public interface

    @renpy.pure
    def Preference(name, value=None):
        """
         :doc: preference_action

         This constructs the appropriate action or value from a preference.
         The preference name should be the name given in the standard
         menus, while the value should be either the name of a choice,
         "toggle" to cycle through choices, a specific value, or left off
         in the case of buttons.

         Actions that can be used with buttons and hotspots are:

         * Preference("display", "fullscreen") - displays in fullscreen mode.
         * Preference("display", "window") - displays in windowed mode at 1x normal size.
         * Preference("display", 2.0) - displays in windowed mode at 2.0x normal size.
         * Preference("display", "any window") - displays in windowed mode at the previous size.
         * Preference("display", "toggle") - toggle display mode.

         * Preference("transitions", "all") - show all transitions.
         * Preference("transitions", "none") - do not show transitions.
         * Preference("transitions", "toggle") - toggle transitions.

         * Preference("show empty window", "show") - Allow the "window show" and "window auto" statement to show an empty window outside of the say statement.
         * Preference("show empty window", "hide") - Prevent the above.
         * Preference("show empty window", "toggle") - Toggle the above.

         * Preference("text speed", 0) - make text appear instantaneously.
         * Preference("text speed", 142) - set text speed to 142 characters per second.

         * Preference("joystick") - Show the joystick preferences.

         * Preference("skip", "seen") - Only skip seen messages.
         * Preference("skip", "all") - Skip unseen messages.
         * Preference("skip", "toggle") - Toggle between skip seen and skip all.

         * Preference("begin skipping") - Starts skipping.

         * Preference("after choices", "skip") - Skip after choices.
         * Preference("after choices", "stop") - Stop skipping after choices.
         * Preference("after choices", "toggle") - Toggle skipping after choices.

         * Preference("auto-forward time", 0) - Set the auto-forward time to infinite.
         * Preference("auto-forward time", 10) - Set the auto-forward time (unit is seconds per 250 characters).

         * Preference("auto-forward", "enable") - Enable auto-forward mode.
         * Preference("auto-forward", "disable") - Disable auto-forward mode.
         * Preference("auto-forward", "toggle") - Toggle auto-forward mode.

         * Preference("auto-forward after click", "enable") - Remain in auto-forward mode after a click.
         * Preference("auto-forward after click", "disable") - Disable auto-forward mode after a click.
         * Preference("auto-forward after click", "toggle") - Toggle auto-forward after click.

         * Preference("automatic move", "enable") - Enable automatic mouse mode.
         * Preference("automatic move", "disable") - Disable automatic mouse mode.
         * Preference("automatic move", "toggle") - Toggle automatic mouse mode.

         * Preference("wait for voice", "enable")  - Wait for the currently playing voice to complete before auto-forwarding.
         * Preference("wait for voice", "disable") - Do not wait for the currently playing voice to complete before auto-forwarding.
         * Preference("wait for voice", "toggle")  - Toggle wait voice.

         * Preference("voice sustain", "enable")  - Sustain voice past the current interaction.
         * Preference("voice sustain", "disable") - Don't sustain voice past the current interaction.
         * Preference("voice sustain", "toggle")  - Toggle voice sustain.

         * Preference("music mute", "enable") - Mute the music mixer.
         * Preference("music mute", "disable") - Un-mute the music mixer.
         * Preference("music mute", "toggle") - Toggle music mute.

         * Preference("sound mute", "enable") - Mute the sound mixer.
         * Preference("sound mute", "disable") - Un-mute the sound mixer.
         * Preference("sound mute", "toggle") - Toggle sound mute.

         * Preference("voice mute", "enable") - Mute the voice mixer.
         * Preference("voice mute", "disable") - Un-mute the voice mixer.
         * Preference("voice mute", "toggle") - Toggle voice mute.

         * Preference("music volume", 0.5) - Set the music volume.
         * Preference("sound volume", 0.5) - Set the sound volume.
         * Preference("voice volume", 0.5) - Set the voice volume.

         * Preference("emphasize audio", "enable") - Emphasize the audio channels found in :var:`config.emphasize_audio_channels`.
         * Preference("emphasize audio", "disable") - Do not emphasize audio channels.
         * Preference("emphasize audio", "toggle") - Toggle emphasize audio.

         * Preference("self voicing", "enable") - Enables self-voicing.
         * Preference("self voicing", "disable") - Disable self-voicing.
         * Preference("self voicing", "toggle") - Toggles self-voicing.

         * Preference("clipboard voicing", "enable") - Enables clipboard-voicing.
         * Preference("clipboard voicing", "disable") - Disable clipboard-voicing.
         * Preference("clipboard voicing", "toggle") - Toggles clipboard-voicing.

         Values that can be used with bars are:

         * Preference("text speed")
         * Preference("auto-forward time")
         * Preference("music volume")
         * Preference("sound volume")
         * Preference("voice volume")
         """

        def show_exception():
            raise Exception("Preference(%r, %r) is unknown." % (name , value))

        name = name.lower()
        if not __preferences.has_key(name):
            show_exception()

        p = __preferences[name]

        if isinstance(value, basestring):
            value = value.lower()

        while True:
            if not p["choices"]:
                 break
            if value in p["choices"]:
                 break
            if p["takes_int"] and isinstance(value, int):
                break
            if p["takes_float"] and isinstance(value, float):
                break
            show_exception()

        rv = p["callfunc"](value)

        if rv is not None:
            rv.alt = name + " [text]"

        return rv


    def registerPreference( name,
                            callfunc,
                            choices = (),
                            takes_float = False,
                            takes_int = False ):
        name = name.lower()
        assert name.startswith('u_')
        __registerPreference(name,choices,calledfunc)


    ## self-voicing display

    def __show_self_voicing():
        has_screen = renpy.get_screen("_self_voicing")

        if _preferences.self_voicing and not has_screen:
            renpy.show_screen("_self_voicing")
        elif not _preferences.self_voicing and has_screen:
            renpy.hide_screen("_self_voicing")

    config.interact_callbacks.append(__show_self_voicing)



init -1500:

    # The screen that we use to indicate that self-voicing is enabled.
    screen _self_voicing():
        zorder 1500

        if _preferences.self_voicing == "clipboard":
            $ message = _("Clipboard voicing enabled. Press 'shift+C' to disable.")
        else:
            $ message = _("Self-voicing enabled. Press 'v' to disable.")

        text message:
            alt ""

            xpos 10
            ypos 35
            color "#fff"
            outlines [ (1, "#0008", 0, 0)]
