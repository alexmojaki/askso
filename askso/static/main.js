'use strict';

var output_editor;
var code_editor;

$(document).ready(function () {
    output_editor = ace.edit("output-editor");
    output_editor.setTheme("ace/theme/monokai");
    output_editor.setShowPrintMargin(false);
    output_editor.on('change', function () {
        $('#next-button').prop('disabled', !output_editor.getValue().trim());
    });

    code_editor = ace.edit("code-editor");
    code_editor.setTheme("ace/theme/monokai");
    code_editor.setShowPrintMargin(false);
    code_editor.getSession().setMode("ace/mode/python");

    function warning(text) {
        return '<div class="alert alert-warning">' +
            '<span class="glyphicon glyphicon-warning-sign"></span> ' + text + '</div>';
    }

    var code_too_long = $(warning('Your code is very long! Try to shorten it.')).hide().prop('id', 'code-too-long');
    $('#code-editor').before(code_too_long);

    code_editor.on('change', function () {
        code_too_long.toggle(code_editor.getSession().getLength() > 50);
        if (step_index == generating_question_step) {
            next_button.prop('disabled', true).val('Run your code again before regenerating the question');
        }
    });
    var json;
    $('#run').click(function () {
        var code_message = $('#code-message').text('Running...').show();
        var results = $('#results').empty();
        var stdin_error = $('#stdin-error').hide();
        $.post('run', code_editor.getValue()).done(function (response) {
            json = JSON.parse(response);
            function warn(text) {
                results.append(warning(text))
            }

            if (json.stdin_used) {
                code_message.hide();
                stdin_error.show();
                return;
            } else if (json.stdout || json.stderr || json.files.length) {
                code_message.hide();
            } else {
                code_message.text('There was no output at all.');
            }
            function add_data(name, data) {
                if (data) {
                    results.append('<p>' + name + ':</p><pre>' + data + '</pre>')
                }
            }

            add_data('Output', json.stdout);
            add_data('Error', json.stderr);
            json.files.forEach(function (file) {
                if (file.data === '') {
                    results.append('<p>The file <code>' + file.path + '</code> is empty.</p>')
                } else {
                    add_data('Contents of the file <code>' + file.path + '</code>', file.data);
                }
            });
            if (json.files.length > 3) {
                warn("You're opening too many different files in your code. This will make your question complicated. " +
                    "Only open as many files as needed to explain your problem. " +
                    "At most 3 files will be displayed here")
            }
            if (json.files.length || json.non_ascii_files.length) {
                warn("Try to avoid using files in your code unless it's strictly related to your question. " +
                    "For example, consider using a list of strings instead of reading from a file, " +
                    "or printing instead of writing to a file. " +
                    "If you really must use files and your code is having trouble finding them, use the full, absolute path.");
            }
            if (json.non_ascii_files.length) {
                warn("Some of the files opened did not consist of only plain ASCII characters and thus cannot " +
                    "be previewed. This may be normal, and it may even be the reason for your question, but if " +
                    "you're handling normal text files (e.g. .txt, .csv, or .html) consider removing exotic characters " +
                    "such as accents or curly quotes for the sake of the question.")
            }
            if (step_index == 1) {
                perform_step();
            }
            if (step_index == generating_question_step) {
                next_button.val(steps[step_index].button_text).prop('disabled', false);
            }
        }).fail(function (response) {
            code_message.hide();
            results.append(
                '<div class="alert alert-danger"><span class="glyphicon glyphicon-exclamation-sign"></span> ' +
                'There was an error on the server!</div>' +
                '<pre>' + response.responseText + '</pre>');
        });
        return false;
    });
    var next_button = $('#next-button');
    var steps = [
        {
            message: "Welcome! I'm going to help you write a good question about Python for StackOverflow.",
            button_text: 'Start'
        },
        {
            extra: function () {
                $('#codearea').show();
            },
            message: "Type in or paste all of your relevant code, and click 'Run'."
        },
        {
            message: 'Click continue when the code is showing the problem you want to ask about.',
            button_text: 'Continue'
        },
        {
            message: 'Is the code as short as possible? Try removing and simplifying as much code as you can without removing the problem. ' +
            'If part of the code is working correctly, replace it with simple statements directly setting variables to the right values.',
            button_text: 'Yes'
        },
        {
            message: "Have you tried your best to solve the problem? Have you searched on Google? Have you printed variables and expressions at different points in your code to see what's happening?",
            button_text: 'Yes'
        },
        {
            message: "What result are you trying to get? Even if you don't want to output anything, include one or more print statements in your code and add the expected output below so that it's absolutely clear what you're trying to do. You can also enter the expected contents of a file.",
            button_text: 'Done',
            extra: function () {
                next_button.prop('disabled', true);
                $('#expected-output').show();
            }
        },
        {
            message: "Congratulations! Here is the basic text of your question. " +
            "Copy it into StackOverflow (if you already have a question, edit it), " +
            "fill in the details, and make any changes you want. " +
            "You can still make changes to the code: just click 'Run' and then 'Regenerate question'.",
            extra: function () {
                function indent(text) {
                    return "\n\n" + text.trim().replace(/^/mg, '    ') + "\n\n";
                }

                function generate_code() {
                    $('#question').show().val(
                        "*Explain what you're trying to do and why*\n\n" +
                        "Here is my code:" + indent(code_editor.getValue()) +
                        (json.stdout ? ("This is the output:" + indent(json.stdout)) : "There is no output. ") +
                        (json.stderr ? ("There is an error:" + indent(json.stderr)) : "No error is raised. ") +
                        json.files.map(function (file) {
                            return file.data ? ("Here are the contents of `" + file.path + "`:" + indent(file.data)) :
                            "`" + file.path + "` is empty. ";
                        }).join('') +
                        "This is the result I want:" + indent(output_editor.getValue()) +
                        "*Maybe add some more explanation and details. Make it clear what you're asking.*\n\n" +
                        "I am running Python " + json.version + ".\n\n" +
                        "----------\n\n" +
                        "*This question was written with the help of [AskSO](https://github.com/alexmojaki/askso).*"
                    );
                }

                generate_code();
                next_button.click(generate_code);
            },
            button_text: 'Regenerate question'
        }
    ];
    var generating_question_step = steps.length - 1;
    var step_index = -1;

    function perform_step() {
        step_index++;
        var step = steps[step_index];
        $('#main-message').text(step.message);
        if (step.button_text) {
            next_button.val(step.button_text);
            next_button.show();
        } else {
            next_button.hide();
        }
        next_button.off('click');
        if (step.extra) {
            step.extra();
        }
        if (step_index < steps.length - 1) {
            next_button.click(perform_step);
        }
    }

    perform_step();
});