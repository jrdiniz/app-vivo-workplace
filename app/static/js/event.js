const statusDropDown = document.getElementById('status-dropdown');


var momentDateFormat = 'DD/MM/YYYY'
var momentMaskDate = IMask(
    document.getElementById('event_date'),
    {
        mask: Date,
        pattern: momentDateFormat,
        lazy: false,
        format: function(date){
            return moment(date).format(momentDateFormat);
        },
        parse: function(str){
            return moment(str, momentDateFormat)
        },
        blocks: {
            DD: {
                mask: IMask.MaskedRange,
                from: 1,
                to: 31,
                maxLength: 2
            },
            MM: {
                mask: IMask.MaskedRange,
                from: 1,
                to: 12,
                maxLength: 2
            },
            YYYY:{
                mask: IMask.MaskedRange,
                from: new Date().getFullYear(),
                to: new Date().getFullYear() + 1,
                maxLength: 4,
            }
        }
    }
);
var momentTimeFormat = 'HH:mm'
var momentMaskTime = IMask(
    document.getElementById('start'),
    {
        mask: Date,
        pattern: momentTimeFormat,
        format:function(date){
            return moment(date).format(momentTimeFormat)
        },
        parse: function(str){
            return moment(str, momentTimeFormat)
        },
        blocks: {
            HH: {
                mask: IMask.MaskedRange,
                from: 0,
                to: 23,
                maxLength: 2
            },
            mm: {
                mask: IMask.MaskedRange,
                from: 0,
                to: 59,
                maxLength: 2
            }
        }
    }
)
var momentTimeFormat = 'HH:mm'
var momentMaskTime = IMask(
    document.getElementById('end'),
    {
        mask: Date,
        pattern: momentTimeFormat,
        format:function(date){
            return moment(date).format(momentTimeFormat)
        },
        parse: function(str){
            return moment(str, momentTimeFormat)
        },
        blocks: {
            HH: {
                mask: IMask.MaskedRange,
                from: 0,
                to: 23,
                maxLength: 2
            },
            mm: {
                mask: IMask.MaskedRange,
                from: 0,
                to: 59,
                maxLength: 2
            }
        }
    }
)
