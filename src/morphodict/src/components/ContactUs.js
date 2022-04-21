import "./style.css";
function ContactUs(props) {
  return (
    <section id="contact-us" className="prose box box--spaced">
      <h2 className="prose__section-title">Contact us</h2>
      <p>
        Email us at&nbsp;
        <a href="mailto:altlab+itwewina@ualberta.ca" className="about__link">
          altlab@ualberta.ca
        </a>
        &nbsp;. Alternatively, you can also use this structured&nbsp;
        <a href="https://docs.google.com/forms/d/e/1FAIpQLSdsBPVPoadoRQEV9ZRKAHbHgolFtmvjWnfpZZYCvX-n2EFwZg/viewform">
          feedback form
        </a>
        .&nbsp;
      </p>
      <p>
        {" "}
        Let us know about any bugs, glitches, issues with the dictionary, or
        incorrect information you find. You can also suggest features and
        improvements.{" "}
      </p>
    </section>
  );
}

export default ContactUs;
