// GET - policy/cookie-policy
module.exports.cookiePolicy = (req, res) => {

    res.render('policy/cookiePolicy', {title: 'cookiePolicy', page: 'cookiePolicy'})

}


// GET - tandc
module.exports.tandc = (req, res) => {

    res.render('policy/tandc', { title: 'longrunner.co.uk Information Page', page: 'tandc' });
}