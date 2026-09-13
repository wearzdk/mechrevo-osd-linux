// SPDX-License-Identifier: GPL-2.0-or-later
/* Linux transport for MECHREVO firmware status events.
 * Pass the EventDetail bytes to userspace. No firmware method calls, no
 * input key injection, no profile/LED/EC writes, and no mode state machine.
 */
#include <linux/dmi.h>
#include <linux/input.h>
#include <linux/module.h>
#include <linux/slab.h>
#include <linux/spinlock.h>
#include <linux/unaligned.h>
#include <linux/wmi.h>

struct event_transport {
	struct input_dev *input;
	spinlock_t lock;
};

static int osd_probe(struct wmi_device *wdev, const void *context)
{
	struct input_dev *input;
	struct event_transport *transport;

	if (!dmi_match(DMI_SYS_VENDOR, "MECHREVO") ||
	    !dmi_match(DMI_BOARD_NAME, "WUJIE Series-T142-HPT-R"))
		return -ENODEV;
	transport = devm_kzalloc(&wdev->dev, sizeof(*transport), GFP_KERNEL);
	if (!transport)
		return -ENOMEM;
	spin_lock_init(&transport->lock);
	input = devm_input_allocate_device(&wdev->dev);
	if (!input)
		return -ENOMEM;
	input->name = "MECHREVO OSD firmware events";
	input->phys = "wmi/osd0";
	input->id.bustype = BUS_HOST;
	input->dev.parent = &wdev->dev;
	/* The two MSC words carry all 8 EventDetail bytes. EV_KEY is absent. */
	input_set_capability(input, EV_MSC, MSC_SERIAL);
	input_set_capability(input, EV_MSC, MSC_RAW);
	transport->input = input;
	dev_set_drvdata(&wdev->dev, transport);
	return input_register_device(input);
}

static void osd_notify(struct wmi_device *wdev, const struct wmi_buffer *buffer)
{
	struct event_transport *transport = dev_get_drvdata(&wdev->dev);
	struct input_dev *input = transport->input;
	const u8 *event = buffer->data;
	unsigned long flags;

	spin_lock_irqsave(&transport->lock, flags);
	input_event(input, EV_MSC, MSC_SERIAL, get_unaligned_le32(event));
	input_event(input, EV_MSC, MSC_RAW, get_unaligned_le32(event + 4));
	input_sync(input);
	spin_unlock_irqrestore(&transport->lock, flags);
}

static const struct wmi_device_id osd_ids[] = {
	{ "46C93E13-EE9B-4262-8488-563BCA757FEF", NULL }, {},
};
/* Deliberately no autoload alias: the binding service selects this driver for
 * this event device, avoiding a boot-time race with redmi-wmi/bitland-mifs-wmi.
 */

static struct wmi_driver osd_driver = {
	.driver = { .name = "mechrevo-osd-wmi" },
	.no_singleton = true,
	.id_table = osd_ids,
	.min_event_size = 8,
	.probe = osd_probe,
	.notify_new = osd_notify,
};
module_wmi_driver(osd_driver);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Read-only firmware event transport for MECHREVO T142-HPT-R");
